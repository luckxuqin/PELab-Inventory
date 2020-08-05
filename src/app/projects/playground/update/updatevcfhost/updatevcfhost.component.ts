import { Component, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Http, Response ,Headers} from '@angular/http';
import { Subject } from 'rxjs';
import { ClrDatagridFilterInterface, ClrDatagridFilter } from '@clr/angular';
import { ClrDatagridStringFilterInterface } from '@clr/angular';
import { ActivatedRoute } from '@angular/router';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { ClrWizard } from '@clr/angular';

@Component({
  selector: 'berry-filter',
  templateUrl: './updatevcfhost.component.html',
  styleUrls: [ './updatevcfhost.component.scss' ],

  // tslint:disable-next-line:use-host-property-decorator
  host: {
    '[class.content-container]': 'true',
  },
})

export class UpdatevcfhostComponent implements OnInit {

  constructor (private readonly http2: HttpClient,
    private readonly http: Http, private route: ActivatedRoute) { }

  @ViewChild('wizard' ) wizard: ClrWizard;

  _open = false;


  httpOptions = {
    headers: new Headers({
      'Access-Control-Allow-Origin': '*',
    }),
  };

  private serverUrl = 'http://localhost:8000/';

  id: string;
  page: string;
  private sub: any;
  selectedHost: any = [];

  cols: string[] = ['Hostname', 'HostIP', 'Status','OEM','Server_Model','Team','AssignTo','TestBed','StartDate','EndDate'];
  cols2: string[] = ['HostIP', 'Status','OEM','Server_Model','Team','AssignTo','TestBed','StartDate','EndDate'];
  data: object[] = [];
  data_vcf: object[] = [];
  data_domain: object[] = [];
  data_cluster: object[] = [];

  updateinfo = {
    Team: '',
    AssignTo: '',
    TestBed: '',
    StartDate: '',
    EndDate: '',
    IS_VCF: '',
    VCF: '',
    Domain: '',
    Cluster: '',
  };

  open () {
    this._open = !this.open;
  }

  doCancel (): void {
    this.wizard.close();
    // console.log(this.updateinfo);
    window.location.reload();
  }

  onCommit (): void {
    console.log(this.selectedHost);
    const body: BodyData = {
      updateinfo: this.updateinfo,
      selectedHosts: this.selectedHost,
    };

    this.put(body);
    window.location.reload();
  }

  put (body: BodyData) {
    console.log(body);
    this.http.put(this.serverUrl + `api/hostsvcf/`, body, this.httpOptions )
    .map((res: Response) => res.json()).subscribe(data => {
      console.log(data);
    });
  }


  getData () {
    return this.http.get(this.serverUrl + `api/hosts`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.data = data.data;
      });
  }

  getVcf () {
    return this.http.get(this.serverUrl + `api/vcf`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.data_vcf = data.data;
      });
  }

  getDomain () {
    return this.http.get(this.serverUrl + `api/domain`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.data_domain = data.data;
      });
  }

  getCluster () {
    return this.http.get(this.serverUrl + `api/cluster`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.data_cluster = data.data;
      });
  }

  ngOnInit () {
    this.getData();
    this.getVcf();
    this.getDomain();
    this.getCluster();
  }
}

export interface BodyData {
  updateinfo: object;
  selectedHosts: object[];
}


