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
* extrinsic-table.component.ts
*/

import { ContractService } from './../../services/contract.service';
import { ContractInstanceService } from 'src/app/services/contract-instance.service';
import { Contract } from './../../classes/contract.class';
import { Component, Input, OnInit } from '@angular/core';
import { ContractMessage, Extrinsic } from '../../classes/extrinsic.class';
import { Location } from '@angular/common';
import { ExtrinsicService } from '../../services/extrinsic.service';
import { switchMap, map } from 'rxjs/operators';
import { of } from 'rxjs';
import _ from 'lodash';
@Component({
  selector: 'app-extrinsic-table',
  templateUrl: './extrinsic-table.component.html',
  styleUrls: ['./extrinsic-table.component.scss']
})
export class ExtrinsicTableComponent implements OnInit {

  @Input() extrinsic: Extrinsic = null;
  @Input() extrinsicId: string = null;
  @Input() context: string = null;
  @Input() networkURLPrefix: string = null;
  @Input() networkTokenDecimals = 0;
  @Input() networkTokenSymbol: string;
  @Input() title: string;

  public contract: Contract;
  public isContractCall: boolean = false;
  public isPrivate: boolean = false;
  public contractAddress: string = '';
  public contractName: string = '';
  public contractSymbol: string = '';
  public contractDecimals = 0;
  constructor(
    private location: Location,
    private extrinsicService: ExtrinsicService,
    private contractInstanceService: ContractInstanceService,
    private contractService: ContractService,
  ) { }

  ngOnInit() {
    const extrinsicRx = this.extrinsicId ? this.extrinsicService.get(this.extrinsicId) : of(this.extrinsic)
    extrinsicRx
      .pipe(map(data => {
        // ---
        console.info('data----', data)
        if (data.attributes.module_id === 'Contracts' && data.attributes.call_id === 'call' && data.attributes.params) {
          this.contractAddress = data.attributes.params[0].value
          this.isContractCall = true
          this.loadContractInfo(data.attributes.params[0].value)
        }
        if (data.attributes.is_private) {
          this.isPrivate = data.attributes.is_private
        }
        const cm = data.attributes.contract_message as ContractMessage
        if (cm) {
          if (!data.attributes.params) data.attributes.params = []
          data.attributes.params.forEach((item) => {
            if (item.name === 'value') {
              item.name = 'Fee'
            }
          })
          if (this.isContractCall) {
            cm.args.forEach((item) => {
              item.type = 'ContractBalance'
            })
          }
          data.attributes.params = data.attributes.params.concat(cm.args)

          if (cm.name) {
            data.attributes.params.push({ name: 'Call', value: cm.name })
          }
        }
        // ---
        const events = data.relationships.events.data
        for (const e of events) {
          const name = _.get(e, 'attributes.contract_event.name', '')
          if (name.includes('Failed')) {
            _.set(data.attributes, 'success', false)
            _.set(data.attributes, 'error', true)
            break;
          }
        }
        return data
      }))
      .subscribe(extrinsic => this.extrinsic = extrinsic);
  }

  loadContractInfo(id): void {
    this.contractInstanceService.get(id).pipe(
      switchMap((data) => {
        if (this.isContractCall) {
          this.contractSymbol = _.get(data.attributes, 'symbol', '')
          this.contractDecimals = _.get(data.attributes, 'decimals', 0)
        }
        return this.contractService.get(data.attributes.code_hash)
      })
    ).subscribe(contract => {
      if (contract && contract.attributes.abi) {
        this.contractName = contract.attributes.abi.contract.name
      }
    })
  }

  goBack(): void {
    this.location.back();
  }

  public formatBalance(balance: number) {
    return balance / Math.pow(10, this.networkTokenDecimals);
  }

  paramName(name: string) {

    if (name === 'dest') {
      name = 'Destination';
    }

    return name;
  }

}
