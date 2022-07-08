/*
 * Polkascan Explorer GUI
 *
 * Copyright 2018-2020 openAware BV (NL).
 * This file is part of Polkascan.
 *
 * Polkascan is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Polkascan is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Polkascan. If not, see <http://www.gnu.org/licenses/>.
 *
 * contract-detail.component.ts
 */
import { Abi, Source, ContractInfo } from './../../classes/contract.class';
import { ContractService } from './../../services/contract.service';
import { Component, OnInit } from '@angular/core';
import {Observable, Subscription} from 'rxjs';
import {Contract} from '../../classes/contract.class';
import {ActivatedRoute, ParamMap} from '@angular/router';
import {switchMap, map} from 'rxjs/operators';
import {AppConfigService} from '../../services/app-config.service';
import { ContractInstanceService } from 'src/app/services/contract-instance.service';

@Component({
  selector: 'app-contract-detail',
  templateUrl: './contract-detail.component.html',
  styleUrls: ['./contract-detail.component.scss']
})
export class ContractDetailComponent implements OnInit {

  public contract$: Observable<Contract>;
  private networkSubscription: Subscription;
  public networkURLPrefix: string;
  public source: Source;
  public info: ContractInfo;
  public isDeployed: boolean;
  constructor(
    private activatedRoute: ActivatedRoute,
    private contractInstanceService: ContractInstanceService,
    private contractService: ContractService,
    private appConfigService: AppConfigService,
  ) { }

  ngOnInit() {
    this.networkSubscription = this.appConfigService.getCurrentNetwork().subscribe( network => {

      this.networkURLPrefix = this.appConfigService.getUrlPrefix();

      this.contract$ = this.activatedRoute.paramMap.pipe(
        switchMap((params: ParamMap) => {
          if (params.get('type') === 'uploaded') {
            this.isDeployed = false
            return this.contractService.get(params.get('id')).pipe(map(c => {
              if (c.attributes.abi) {
                this.source = c.attributes.abi.source
                this.info = c.attributes.abi.contract
              }
              return c
            }))
          }
          this.isDeployed = true
          return this.contractInstanceService.get(params.get('id')).pipe(
            switchMap((contractInstance) => {
              return this.contractService.get(contractInstance.attributes.code_hash).pipe(map(c => {
                if (c.attributes.abi) {
                  this.source = c.attributes.abi.source
                  this.info = c.attributes.abi.contract
                }
                return contractInstance
              }))
            })
          );
        }),
      );
    });
  }

  formatStr(account: string, count = 6) {
    if (!account) {
      return account
    }
    if (account.length <= (count * 2))
      return account
    return `${account.substring(0, count)}...${account.substring(account.length - count)}`
  }
}
