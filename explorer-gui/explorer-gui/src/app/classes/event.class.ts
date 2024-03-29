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
 * event.class.ts
 */

import { Resource } from 'ngx-jsonapi';

export interface EventType {
  type: number,
  displayName: string[]
}

export interface EventArgs {
  name: string,
  value: string | number,
  type: EventType
}

export interface ContractEvent {
  args: EventArgs[],
}
export class Event extends Resource {
  public attributes = {
    block_id: 'block_id',
    module_id: 'module_id',
    event_id: 'event_id',
    extrinsic_idx: 'extrinsic_idx',
    attributes: 'attributes',
    params: 'params',
    contract_event: {},
    is_private: false
  };
}
