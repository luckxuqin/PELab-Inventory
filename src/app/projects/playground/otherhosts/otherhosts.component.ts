import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Http, Response } from '@angular/http';
import { Subject } from 'rxjs';
import { ClrDatagridFilterInterface, ClrDatagridFilter } from '@clr/angular';
import { ClrDatagridStringFilterInterface } from '@clr/angular';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'berry-filter',
  templateUrl: './otherhosts.component.html',
  styleUrls: [ './otherhosts.component.scss' ],

  // tslint:disable-next-line:use-host-property-decorator
  host: {
    '[class.content-container]': 'true',
  },
})

export class OtherhostsComponent implements OnInit {

  constructor (private readonly http2: HttpClient,
    private readonly http: Http, private route: ActivatedRoute) { }

  private serverUrl = 'http://localhost:8000/';

  id: string;
  page: string;
  private sub: any;

  cols: string[] = ['Hostname', 'HostIP', 'Status','OEM','Server_Model','Team','AssignTo','TestBed','StartDate','EndDate'];
  cols2: string[] = ['HostIP', 'Status','OEM','Server_Model','Team','AssignTo','TestBed','StartDate','EndDate'];
  data: object[] = [];
  cores: number;
  nic: string;
  disk: string;
  nic_size = 0;
  cpucheck = false;
  diskcheck = true;
  niccheck = false;


  getData () {
    return this.http.get(this.serverUrl + `api/hosts`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.data = data.data;
      });
  }

  CPUfilter () {
    console.log(this.cores);
    if ( this.cores != null ) {
      return this.http.get(this.serverUrl + `api/cores/${this.cores}`)
        .map((res: Response) => res.json()).subscribe(data => {
          console.log(data);
          this.data = data.data;
        });
    } else {
      return this.http.get(this.serverUrl + `api/hosts`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.data = data.data;
      });
    }
  }

  NICfilter () {
    console.log(this.nic);
    if ( this.nic != null) {
      this.nic_size = parseInt(this.nic.substring(0, 2), 10);
      console.log(this.nic_size);
    }
  }

  Filter () {
    if ( this.nic != null) {
      this.nic_size = parseInt(this.nic.substring(0, 2), 10);
     // console.log(this.nic_size);
    }
    const address = this.serverUrl + `api/filter/${!this.cpucheck}/${this.cores}/${!this.niccheck}/${this.nic_size}`;
    console.log(this.disk);
    return this.http.get(this.serverUrl + `api/filter/${!this.cpucheck}/${this.cores}/${!this.niccheck}/${this.nic_size}`)
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
