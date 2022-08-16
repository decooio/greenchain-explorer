import { Component, OnDestroy, OnInit } from "@angular/core";

@Component({
  selector: "app-dashboard",
  templateUrl: "./cidquery.component.html",
  styleUrls: ["./cidquery.component.scss"],
})
export class CidQueryComponent implements OnInit, OnDestroy {
  cid: string;

  ngOnDestroy(): void {}
  ngOnInit(): void {}
  search(): void {
    // Strip whitespace from search text
    console.log(this.cid);
  }
}
