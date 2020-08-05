import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SharedSpecModule } from '../../../shared/shared.module';

import { VlanComponent } from './vlan.component';

describe('VlanComponent', () => {
  let component: VlanComponent;
  let fixture: ComponentFixture<VlanComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [ SharedSpecModule ],
      declarations: [ VlanComponent ],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VlanComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});

