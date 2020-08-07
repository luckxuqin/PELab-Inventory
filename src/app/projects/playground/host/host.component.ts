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
  templateUrl: './host.component.html',
  styleUrls: [ './host.component.scss' ],

  // tslint:disable-next-line:use-host-property-decorator
  host: {
    '[class.content-container]': 'true',
  },
})

export class HostComponent implements OnInit {

  constructor (private readonly http2: HttpClient,
    private readonly http: Http, private route: ActivatedRoute) { }

  private serverUrl = HomeComponent.serverUrl;
  // private SSG_2027R_AR24NV = require('assets/images/SSG-2027R-AR24NV.png');

  id = '';
  page = '';
  private sub: any;

  cols: string[] = ['Hostname','HostIP','Status','OEM','Server_Model','Team','AssignTo','TestBed','StartDate','EndDate'];
  // data: object[] = [];
  record: object[] = [];


  cols_vcf: string[] = [ 'VCF', 'SDDC', 'Username', 'Password' ];
  data_vcf: object[] = [];

  nic_host: string[] = [ 'NIC1', 'NIC2', 'NIC3', 'NIC4', 'NIC5', 'NIC6' ];

  dic_nic = {
    'NIC1': [ 'NIC_1_Description', 'NIC_1_Speed', 'NIC_1_Link' ],
    'NIC2': [ 'NIC_2_Description', 'NIC_2_Speed', 'NIC_2_Link' ],
    'NIC3': [ 'NIC_3_Description', 'NIC_3_Speed', 'NIC_3_Link' ],
    'NIC4': [ 'NIC_4_Description', 'NIC_4_Speed', 'NIC_4_Link' ],
    'NIC5': [ 'NIC_5_Description', 'NIC_5_Speed', 'NIC_5_Link' ],
    'NIC6': [ 'NIC_6_Description', 'NIC_6_Speed', 'NIC_6_Link' ],
  };

  dic_nic2 = {
    'NIC1': 'NIC_1_Description',
    'NIC2': 'NIC_2_Description',
    'NIC3': 'NIC_3_Description',
    'NIC4': 'NIC_4_Description',
    'NIC5': 'NIC_5_Description',
    'NIC6': 'NIC_6_Description',
  };

  disk_host: string[] = [ 'Disk 1', 'Disk 2', 'Disk 3', 'Disk 4', 'Disk 5', 'Disk 6',
    'Disk 7', 'Disk 8', 'Disk 9', 'Disk 10', 'Disk 11', 'Disk 12',
    'Disk 13', 'Disk 14', 'Disk 15', 'Disk 16', 'Disk 17', 'Disk 18',
    'Disk 19', 'Disk 20', 'Disk 21', 'Disk 22', 'Disk 23', 'Disk 24', 'Disk 25',
  ];

  dic_disk = {
    'Disk 1': [ 'HD_1_Vendor', 'HD_1_Model', 'HD_1_Size' ],
    'Disk 2': [ 'HD_2_Vendor', 'HD_2_Model', 'HD_2_Size' ],
    'Disk 3': [ 'HD_3_Vendor', 'HD_3_Model', 'HD_3_Size' ],
    'Disk 4': [ 'HD_4_Vendor', 'HD_4_Model', 'HD_4_Size' ],
    'Disk 5': [ 'HD_5_Vendor', 'HD_5_Model', 'HD_5_Size' ],
    'Disk 6': [ 'HD_6_Vendor', 'HD_6_Model', 'HD_6_Size' ],
    'Disk 7': [ 'HD_7_Vendor', 'HD_7_Model', 'HD_7_Size' ],
    'Disk 8': [ 'HD_8_Vendor', 'HD_8_Model', 'HD_8_Size' ],
    'Disk 9': [ 'HD_9_Vendor', 'HD_9_Model', 'HD_9_Size' ],
    'Disk 10': [ 'HD_10_Vendor', 'HD_10_Model', 'HD_10_Size' ],
    'Disk 11': [ 'HD_11_Vendor', 'HD_11_Model', 'HD_11_Size' ],
    'Disk 12': [ 'HD_12_Vendor', 'HD_12_Model', 'HD_12_Size' ],
    'Disk 13': [ 'HD_13_Vendor', 'HD_13_Model', 'HD_13_Size' ],
    'Disk 14': [ 'HD_14_Vendor', 'HD_14_Model', 'HD_14_Size' ],
    'Disk 15': [ 'HD_15_Vendor', 'HD_15_Model', 'HD_15_Size' ],
    'Disk 16': [ 'HD_16_Vendor', 'HD_16_Model', 'HD_16_Size' ],
    'Disk 17': [ 'HD_17_Vendor', 'HD_17_Model', 'HD_17_Size' ],
    'Disk 18': [ 'HD_18_Vendor', 'HD_18_Model', 'HD_18_Size' ],
    'Disk 19': [ 'HD_19_Vendor', 'HD_19_Model', 'HD_19_Size' ],
    'Disk 20': [ 'HD_20_Vendor', 'HD_20_Model', 'HD_20_Size' ],
    'Disk 21': [ 'HD_21_Vendor', 'HD_21_Model', 'HD_21_Size' ],
    'Disk 22': [ 'HD_22_Vendor', 'HD_22_Model', 'HD_22_Size' ],
    'Disk 23': [ 'HD_23_Vendor', 'HD_23_Model', 'HD_23_Size' ],
    'Disk 24': [ 'HD_24_Vendor', 'HD_24_Model', 'HD_24_Size' ],
    'Disk 25': [ 'HD_25_Vendor', 'HD_25_Model', 'HD_25_Size' ],
  };

  dic_disk2 = {
    'Disk 1': 'HD_1_Vendor',
    'Disk 2': 'HD_2_Vendor',
    'Disk 3': 'HD_3_Vendor',
    'Disk 4': 'HD_4_Vendor',
    'Disk 5': 'HD_5_Vendor',
    'Disk 6': 'HD_6_Vendor',
    'Disk 7': 'HD_7_Vendor',
    'Disk 8': 'HD_8_Vendor',
    'Disk 9': 'HD_9_Vendor',
    'Disk 10': 'HD_10_Vendor',
    'Disk 11': 'HD_11_Vendor',
    'Disk 12': 'HD_12_Vendor',
    'Disk 13': 'HD_13_Vendor',
    'Disk 14': 'HD_14_Vendor',
    'Disk 15': 'HD_15_Vendor',
    'Disk 16': 'HD_16_Vendor',
    'Disk 17': 'HD_17_Vendor',
    'Disk 18': 'HD_18_Vendor',
    'Disk 19': 'HD_19_Vendor',
    'Disk 20': 'HD_20_Vendor',
    'Disk 21': 'HD_21_Vendor',
    'Disk 22': 'HD_22_Vendor',
    'Disk 23': 'HD_23_Vendor',
    'Disk 24': 'HD_24_Vendor',
    'Disk 25': 'HD_25_Vendor',
  };

  // record : object;
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
  }

  getVcf (page: string) {
    if (page === 'home') {
      this.http2.get<ExcelData>('/api/get-vcf')
      .subscribe(res => {
        this.data_vcf = res.data;
        // this.cols = Object.keys(res.cols);
      });
    } else {
      this.http2.get<ExcelData>('/api/get-vcf/' + page)
      .subscribe(res => {
        this.data_vcf = res.data;
        // this.cols = Object.keys(res.cols);
      });
    }
  }*/

  getData (name: string) {
    return this.http.get(this.serverUrl + `api/hosts/${name}`)
      .map((res: Response) => res.json()).subscribe(data => {
        console.log(data);
        this.record = data.data;
      });
  }

  ngOnInit () {
    this.sub = this.route.params.subscribe(params => {
      this.id = params['id'];

        // In a real app: dispatch action to load the details here.
    });
    // this.getExcel(this.page);
    // this.getVcf(this.page);
    // this.record = this.data[this.id];
    this.getData(this.id);
  }
}

export interface ExcelData {
  cols: object;
  data: object[];
}
