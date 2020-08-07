import { Component, OnInit } from '@angular/core';
import { Http, Response } from '@angular/http';
import { HomeComponent } from '../home/home.component';

@Component({
  selector: 'berry-filter',
  templateUrl: './vlan.component.html',
  styleUrls: [ './vlan.component.scss' ],

  // tslint:disable-next-line:use-host-property-decorator
  host: {
    '[class.content-container]': 'true',
  },
})

export class VlanComponent implements OnInit {

  constructor (private readonly http: Http) { }

  private serverUrl = HomeComponent.serverUrl;

  cols: string[] = [ 'Name', '802.1Q Tag', 'MAC-limit', 'Virtual router' ];
  data: object[] = [];

  getData () {
    return this.http.get(this.serverUrl + `api/vlan`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.data = data.data;
      });
  }


  ngOnInit () {
    this.getData();
  }
}

export interface ExcelData {
  cols: object;
  data: object[];
}
