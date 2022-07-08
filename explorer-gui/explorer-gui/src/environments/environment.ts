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
 * environment.ts
 */

// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
// NETWORK_NAME: GreenChain
// NETWORK_ID: greenchain
// NETWORK_TYPE: pre
// CHAIN_TYPE: para
// NETWORK_TOKEN_SYMBOL: GRN
// NETWORK_TOKEN_DECIMALS: 18
// NETWORK_COLOR_CODE: 777777
// API_URL: http://127.0.0.1:8080/api/v1
export const environment = {
  production: false,
  // jsonApiDiscoveryRootUrl: 'https://discovery-31.polkascan.io',
  jsonApiDiscoveryRootUrl: null,
  jsonApiRootUrl: 'https://explorer.greenchain.cc/api/v1',
  // jsonApiRootUrl: 'http://localhost:8080/api/v1',
  network: {
    name: 'GreenChain',
    networkId: 'greenchain',
    networkType: 'pre',
    chainType: 'para',
    tokenSymbol: 'GRN',
    tokenDecimals: 18,
    colorCode: '777777'
  }
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/dist/zone-error';  // Included with Angular CLI.
