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
 * event-table.component.ts
 */

import {Component, Input, OnInit} from '@angular/core';
import {Location} from '@angular/common';
import {Event, ContractEvent, EventArgs} from '../../classes/event.class';
import {Arg} from '../../classes/extrinsic.class';
import {EventService} from '../../services/event.service';
import _ from 'lodash';
import {Observable} from 'rxjs';

@Component({
  selector: 'app-event-table',
  templateUrl: './event-table.component.html',
  styleUrls: ['./event-table.component.scss']
})
export class EventTableComponent implements OnInit {

  @Input() event: Event = null;
  @Input() eventId: string = null;
  @Input() context: string = null;
  @Input() networkURLPrefix: string = null;
  @Input() networkTokenDecimals: number = 0;
  @Input() networkTokenSymbol: string = '';

  public containsParams = false;
  public attributeSuccess = false;
  public isContractCall = false;
  public isPrivate = false;
  public contractSymbol: string = '';
  public contractDecimals = 0;
  constructor(
    private location: Location,
    private eventService: EventService
  ) { }

  ngOnInit() {
    if (this.event) {
      console.log('event not empty')
    } else {
      console.log('event is empty')
      console.log(this.event)
      if (this.eventId) {
        this.eventService.get(this.eventId).subscribe(event => {
          if (event) {
            this.event = event;
          }
        });
      }
    }
  }

  parseParams = (event: Event) => {

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

  setParams() {
    if (this.event.attributes.module_id === 'contracts' && this.event.attributes.event_id === 'ContractExecution') {
      this.containsParams = true
      this.isContractCall = true
      const contractEvent = this.event.attributes.contract_event as ContractEvent
      this.contractSymbol = _.get(this.event.attributes, 'symbol', '')
      this.contractDecimals = _.get(this.event.attributes, 'decimals', 0)
      this.isPrivate = _.get(this.event.attributes.is_private, false)
      if (contractEvent.args) {
        const params = _.map(contractEvent.args, (i: EventArgs) => {
          const type = _.isEmpty(i.type.displayName) ? '' : i.type.displayName[0]
          const arg: Arg = {
            name: i.name,
            value: i.value,
            type: type === 'Balance' ? 'ContractBalance' : type
          }
          return arg;
        })
        this.event.attributes.params = params;
      }
    } else {
      this.event.attributes.params = this.event.attributes.attributes;
    }
    this.attributeSuccess = true;
  }

}
