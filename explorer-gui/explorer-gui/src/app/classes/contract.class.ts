
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
 * contract.class.ts
 */

import { Resource } from 'ngx-jsonapi';

export interface Source {
  hash: string;
  language: string;
  compiler: string;
}
export interface ContractInfo {
  name: string;
  version: string;
  authors: string[];
}

export interface Abi {
  source: Source;
  contract: ContractInfo;
}
export class Contract extends Resource {
  public attributes: {
    created_at_block: number,
    created_at_event: number,
    owner: string,
    code_hash?: string,
    address?: string,
    source?: Source,
    bytecode?: string,
    name: string,
    symbol: string,
    create_time: number,
    abi?: Abi,
    contract?: ContractInfo,
  } = {
      created_at_block: 0,
      created_at_event: 0,
      owner: '-',
      name: '-',
      symbol: '-',
      create_time: 0
    };
}

