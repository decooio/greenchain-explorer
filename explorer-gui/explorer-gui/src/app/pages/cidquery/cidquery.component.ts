import { Component, OnDestroy, OnInit } from "@angular/core";
import { ApiPromise, WsProvider } from "@polkadot/api";
import { ContractPromise } from "@polkadot/api-contract";
import metadata from "../../../assets/metadata.json";
import { HttpClient } from "@angular/common/http";

@Component({
  selector: "app-dashboard",
  templateUrl: "./cidquery.component.html",
  styleUrls: ["./cidquery.component.scss"],
})
export class CidQueryComponent implements OnInit, OnDestroy {
  cid: string;
  searchLoad: boolean = false;
  contract: ContractPromise;
  mainCid: string[] = [];
  thisPdfCid: string = "";
  childCidList: string[] = [];

  constructor(private httpClient: HttpClient) {}
  ngOnDestroy(): void {
    console.log(this.contract);
  }
  ngOnInit(): void {
    console.log(1);
    this.connect();
  }
  async search(): Promise<void> {
    if (this.cid.length > 0) {
      this.searchLoad = true;
    } else {
      return;
    }
    const { gasRequired, storageDeposit, result, output } =
      await this.contract.query.getPdfCid("", {}, [this.cid]);
    if (result.isOk) {
      this.mainCid = output.toHuman() as string[];
      this.thisPdfCid = this.cid;
      this.getChildCid(this.mainCid[0]);
    } else {
      console.error("Error", result.asErr);
    }
    this.searchLoad = false;
  }

  async connect(): Promise<void> {
    const wsProvider = new WsProvider("wss://rpc.greenchain.cc");
    const api = (await ApiPromise.create({ provider: wsProvider })) as any;
    const contract = new ContractPromise(
      api,
      metadata,
      "5F3RW9aKFUWfh894wZn2rd3R6yNz6gVRnDLJ3YsDByP2keCz"
    );
    this.contract = contract;
  }

  getChildCid = (cid: string) => {
    this.httpClient
      .get(`http://1.116.126.237/ipfs/${cid}`)
      .subscribe((res: any) => {
        this.childCidList = res;
      });
  };
}
