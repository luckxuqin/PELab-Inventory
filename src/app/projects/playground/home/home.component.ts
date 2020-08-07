import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Http, Response } from '@angular/http';
import { Subject } from 'rxjs';
import { ClrDatagridFilterInterface, ClrDatagridFilter } from '@clr/angular';
import { ClrDatagridStringFilterInterface } from '@clr/angular';
import { ActivatedRoute } from '@angular/router';
declare var require: any;

@Component({
  selector: 'berry-filter',
  templateUrl: './home.component.html',
  styleUrls: [ './home.component.scss' ],

  // tslint:disable-next-line:use-host-property-decorator
  host: {
    '[class.content-container]': 'true',
  },
})


export class HomeComponent implements OnInit {
  public static serverUrl = 'http://10.156.166.112:8000/';

  constructor (private readonly http2: HttpClient,
    private readonly http: Http, private route: ActivatedRoute) { }
  private myFilter = new MyFilter();
  private sub: any;
  id: string;
  showReserve = false;
  showFree = false;
  showReport = false;

  vo = {
    team: '',
    name: '',
    project: '',
    startDate: '',
    endDate: '',
    server: '',
  };

  sta = {
    status: '',
    server: '',
  };


  cols_vcf: string[] = [ 'Name', 'SDDC', 'Username', 'Password', 'Owner' ];
  data_vcf: object[] = [];
  data_domain: object[] = [];

  getVcf () {
    return this.http.get(HomeComponent.serverUrl + 'api/vcf')
        .map((res: Response) => res.json()).subscribe(data => {
          console.log(data);
          this.data_vcf = data.data;
        });
  }

  getDomain () {
    return this.http.get(HomeComponent.serverUrl + `api/domain`)
        .map((res: Response) => res.json()).subscribe(data => {
          console.log(data);
          this.data_domain = data.data;
        });
  }


  ngOnInit () {
    // this.getExcel(this.id);
    // this.getVcf(this.id);
    // this.getVcfServer();
    this.getVcf();
    this.getDomain();
    // this.http.get<ExcelData>('/api/get-excel')
    //   .subscribe(res => {
    //     this.data = res.data;
    //     //this.cols = Object.keys(res.cols);
    //   });
  }

}

export interface ExcelData {
  cols: object;
  data: object[];
}

export interface Record {
  Hostname: string;
  HostIP: string;
  Status: string;
}

export class MyFilter implements ClrDatagridStringFilterInterface<Record> {
  changes = new Subject<any>();
  isActive (): boolean {
    return true;
  }
  accepts (status: Record, search: string): boolean {
    return '' + status.Status === search || status.Status.toLowerCase().indexOf(search) >= 0;
  }
}
