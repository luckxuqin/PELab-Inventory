import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Http, Response } from '@angular/http';
import { Subject } from 'rxjs';
import { ClrDatagridFilterInterface, ClrDatagridFilter } from '@clr/angular';
import { ClrDatagridStringFilterInterface } from '@clr/angular';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'berry-filter',
  templateUrl: './vcf.component.html',
  styleUrls: [ './vcf.component.scss' ],

  // tslint:disable-next-line:use-host-property-decorator
  host: {
    '[class.content-container]': 'true',
  },
})

export class VcfComponent implements OnInit {

  constructor (private readonly http2: HttpClient,
    private readonly http: Http, private route: ActivatedRoute) { }

  id: string;
  page: string;
  private sub: any;

  private serverUrl = 'http://localhost:8000/';

  cols: string[] = ['HostIP','Status','OEM','Server_Model','Team','AssignTo','TestBed','StartDate','EndDate'];
  data: object[] = [];
  vcf: object[] = [];

  cols_vcf: string[] = [ 'VCF', 'SDDC', 'Username', 'Password' ];

  data_vcf: object[] = [];
  data_domain_mgmt: Domain[] = [];
  data_domain_wkld: Domain[] = [];
  clusters: Cluster[] = [];

  getData (name: string) {
    return this.http.get(this.serverUrl + `api/vcf/${name}`)
        .map((res: Response) => res.json()).subscribe(data => {
          console.log(data);
          this.vcf = data.data;
        });
  }

  getDomainManagement (name: string) {
    return this.http.get(this.serverUrl + `api/domain/${name}/Management`)
        .map((res: Response) => res.json()).subscribe(data => {
          // console.log(data);
          this.data_domain_mgmt = data.data;
          console.log(this.data_domain_mgmt);
          this.getClusterMgmt(name);
        });
  }

  getDomainWorkload (name: string) {
    this.http.get(this.serverUrl + `api/domain/${name}/Workload`)
        .map((res: Response) => res.json()).subscribe(data => {
          // console.log(data);
          this.data_domain_wkld = data.data;
          console.log(this.data_domain_wkld);
          this.getCluster(name);
        });
  }

  getClusterMgmt( vcf: string ) {
    this.http.get(this.serverUrl + `api/cluster/${vcf}/${this.data_domain_mgmt[0].Domain_Name}`)
        .map((res: Response) => res.json()).subscribe(data => {
          for (const cluster of data.data) {
            this.clusters.push(cluster);
          }
          // this.data_domain_wkld = data.data;
        });
  }
  getCluster (vcf: string) {
    /*this.http.get(this.serverUrl + `api/cluster/${vcf}/${this.data_domain_mgmt[0].Domain_Name}`)
        .map((res: Response) => res.json()).subscribe(data => {
          console.log(data);
          // this.data_domain_wkld = data.data;
        });*/
    for ( const domain of this.data_domain_wkld) {
      this.http.get(this.serverUrl + `api/cluster/${vcf}/${domain.Domain_Name}`)
        .map((res: Response) => res.json()).subscribe(data => {
          for (const cluster of data.data) {
            this.clusters.push(cluster);
          }
          // this.data_domain_wkld = data.data;
        });
    }
  }

  ngOnInit () {
    this.sub = this.route.params.subscribe(params => {
      this.id = params['id'];

        // In a real app: dispatch action to load the details here.
    });
    // this.getExcel(this.page);
    // this.getVcf(this.page);
    // this.getExcel();
    // this.getVcf();
    this.getData(this.id);
    this.getDomainManagement(this.id);
    this.getDomainWorkload(this.id);
  }
}

export interface Domain {
  Domain_Name: string;
  Vcf: string;
  Type: string;
  Cluster_Num: string;
  Domain_ID: number;
}

export interface Cluster {
  Cluster_Name: string;
  Vcf: string;
  Domain: string;
  Host_Num: string;
  Cluster_ID: number;
}
