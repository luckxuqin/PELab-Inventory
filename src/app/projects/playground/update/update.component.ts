import { Component, OnInit, ViewChild } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { ClrWizard } from '@clr/angular';
import { Http, Response, Headers } from '@angular/http';
import { Subject } from 'rxjs';
import { ClrDatagridFilterInterface, ClrDatagridFilter } from '@clr/angular';
import { ClrDatagridStringFilterInterface } from '@clr/angular';
import { ActivatedRoute } from '@angular/router';
import { HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'berry-filter',
  templateUrl: './update.component.html',
  styleUrls: [ './update.component.scss' ],

  // tslint:disable-next-line:use-host-property-decorator
  host: {
    '[class.content-container]': 'true',
  },
})

export class UpdateComponent implements OnInit {

  constructor (
    private readonly http: Http, private route: ActivatedRoute) { }

  @ViewChild('wizard' ) wizard: ClrWizard;

  _open = false;

  private serverUrl = 'http://localhost:8000/';
  httpOptions = {
    headers: new Headers({
      'Access-Control-Allow-Origin': '*',
    }),
  };

  disable = true;

  data: object[] = [];
  selectedVCF: any = [];
  cols_vcf: string[] = [ 'Name', 'SDDC', 'Username', 'Password', 'Owner' ];
  vcf: VCFinfo = {
    Name: '',
    SDDC: '',
    Username: '',
    Password: '',
    Owner: '',
    Vcf_ID: '',
  };

  domain_mgmt: Domain;
  domain_wkld: Domain [] = [];
  clusters: Cluster [] = [];

  // data: object[] = [];

  data_domain: Domain[] = [];
  data_cluster: Cluster[] = [];
  num_domains: number;
  workload_index: number [] = [ 0 ];

  open () {
    this._open = !this.open;
  }

  doCancel (): void {
    this.wizard.close();
    window.location.reload();
  }

  post (domains: Domain[]) {
    const data: UpdatedData = {
      VCFinfo: this.vcf,
      Domains: domains,
    };
    console.log(data);
    this.http.post(this.serverUrl + `api/vcf/`, data, this.httpOptions )
    .map((res: Response) => res.json()).subscribe(data => {
      // console.log(data);
    });
  }

  onCommit (): void {
    const domains = this.domain_wkld;
    this.domain_mgmt.Type = 'Management';
    for ( let wkld of domains) {
      wkld.Type = 'Workload';
    }
    domains.push(this.domain_mgmt);
    // console.log(this.vcf);
    // console.log(domains);
    this.post(domains);

    // window.location.reload();
  }


  addClusterMgmt () {
    this.domain_mgmt.clusters.push(this.idle_cluster());
    this.domain_mgmt.Cluster_Num = Number(this.domain_mgmt.Cluster_Num) + 1;
  }
  addClusterWkld (index: number ) {
    this.domain_wkld[index].clusters.push(this.idle_cluster());
    this.domain_wkld[index].Cluster_Num = Number(this.domain_wkld[index].Cluster_Num) + 1;
  }
  addWkldDomain () {
    this.domain_wkld.push(this.idle_domain());
    this.workload_index.push(this.workload_index.length);
  }


  copy () {
    this.domain_wkld = [];
    this.workload_index = [];
    // console.log(this.selectedVCF);
    this.vcf = this.selectedVCF;
    this.disable = false;
    for (const domain of this.data_domain) {
      if ( domain.Vcf === this.selectedVCF.Name) {
        // this.domains.push(domain);
        let cluster_test: Cluster[] = [];
        for (const cluster of this.data_cluster) {
          if ( cluster.Vcf === this.selectedVCF.Name && cluster.Domain === domain.Domain_Name) {
            cluster_test.push(cluster);
          }
        }
        if (domain.Type === 'Workload') {
          this.domain_wkld.push({
            Domain_Name: domain.Domain_Name,
            Vcf: domain.Vcf,
            Type: domain.Type,
            Cluster_Num: domain.Cluster_Num,
            Domain_ID: domain.Domain_ID,
            clusters: cluster_test,
          });
          this.workload_index.push(this.workload_index.length);
        } else {
          this.domain_mgmt = {
            Domain_Name: domain.Domain_Name,
            Vcf: domain.Vcf,
            Type: domain.Type,
            Cluster_Num: domain.Cluster_Num,
            Domain_ID: domain.Domain_ID,
            clusters: cluster_test,
          };
        }
      }
    }
    // console.log(this.domain_mgmt);
    // console.log(this.domain_wkld);
    // console.log(this.workload_index);
    // console.log(this.clusters);
    this.num_domains = this.domain_wkld.length + 1;
    // console.log(this.num_domains);
  }

  idle_domain () {
    const idle: Domain = {
      Domain_Name: '',
      Vcf: '',
      Type: '',
      Cluster_Num: 1,
      Domain_ID: 0,
      clusters: [ {
        Cluster_Name: '',
        Vcf: '',
        Domain: '',
        Host_Num: '',
        Cluster_ID: 0,
      } ],
    };
    return idle;
  }

  idle_cluster () {
    const idle: Cluster = {
      Cluster_Name: '',
      Vcf: '',
      Domain: '',
      Host_Num: '',
      Cluster_ID: 0,
    };
    return idle;
  }

  getData () {
    return this.http.get(this.serverUrl + `api/vcf`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.data = data.data;
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
    this.num_domains = 2;
    this.getData();
    this.getDomain();
    this.getCluster();
    this.domain_mgmt = this.idle_domain();
    this.domain_wkld.push(this.idle_domain());
  }
}

export interface ExcelData {
  cols: object;
  data: object[];
}

export interface UpdatedData {
  Domains: Domain[];
  VCFinfo: VCFinfo;
}

export interface VCFinfo {
  Name: string;
  SDDC: string;
  Username: string;
  Password: string;
  Owner: string;
  Vcf_ID: string;
}

export interface Domain {
  Domain_Name: string;
  Vcf: string;
  Type: string;
  Cluster_Num: number;
  Domain_ID: number;
  clusters: Cluster[];
}

export interface Cluster {
  Cluster_Name: string;
  Vcf: string;
  Domain: string;
  Host_Num: string;
  Cluster_ID: number;
}

