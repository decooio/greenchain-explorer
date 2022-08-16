import { Component, OnDestroy, OnInit } from "@angular/core";
import { ApiPromise, WsProvider, Keyring } from "@polkadot/api";

@Component({
  selector: "app-dashboard",
  templateUrl: "./cidquery.component.html",
  styleUrls: ["./cidquery.component.scss"],
})
export class CidQueryComponent implements OnInit, OnDestroy {
  cid: string;
  searchLoad:boolean = false;

  ngOnDestroy(): void {
    console.log(1);
    
  }
  ngOnInit(): void {

  }
  search(): void {
    // Strip whitespace from search text
    console.log(this.cid);
    if(this.cid.length > 0){
      this.searchLoad = true;
    }else{
      this.searchLoad = false;
    }
  }
}
