import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Http, Response } from '@angular/http';
import { Subject } from 'rxjs';
import { ClrDatagridFilterInterface, ClrDatagridFilter } from '@clr/angular';
import { ClrDatagridStringFilterInterface } from '@clr/angular';
import { ActivatedRoute } from '@angular/router';
import { HomeComponent } from '../home/home.component';

@Component({
  selector: 'berry-filter',
  templateUrl: './cluster.component.html',
  styleUrls: [ './cluster.component.scss' ],

  // tslint:disable-next-line:use-host-property-decorator
  host: {
    '[class.content-container]': 'true',
  },
})

export class ClusterComponent implements OnInit {

  constructor (private readonly http2: HttpClient,
    private readonly http: Http, private route: ActivatedRoute) { }

  private serverUrl = HomeComponent.serverUrl;

  id: string;
  page: string;
  private sub: any;

  cols: string[] = ['HostIP','Cluster', 'Status','OEM','Server_Model','Team','AssignTo','TestBed','StartDate','EndDate'];
  data: object[] = [];

  /*getExcel (page: string) {
    if (page === 'home') {
      this.http2.get<ExcelData>('/api/get-excel')
      .subscribe(res => {
        this.data = res.data;
        // this.cols = Object.keys(res.cols);
      });
    } else {
      this.http2.get<ExcelData>('/api/get-excel/' + page)
      .subscribe(res => {
        this.data = res.data;
        // this.cols = Object.keys(res.cols);
      });
    }
  }*/

  getData (id: string, name: string) {
    return this.http.get(this.serverUrl + `api/host_by_domain/${name}`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.data = data.data;
      });
  }

  ngOnInit () {
    this.sub = this.route.params.subscribe(params => {
      this.id = params['id'];

    });
    // this.getExcel(this.page, this.id);
    this.getData(this.page, this.id);
  }
}

export interface ExcelData {
  cols: object;
  data: object[];
}
