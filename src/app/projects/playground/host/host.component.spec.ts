import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SharedSpecModule } from '../../../shared/shared.module';

import { HostComponent } from './host.component';

describe('HostComponent', () => {
  let component: HostComponent;
  let fixture: ComponentFixture<HostComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [ SharedSpecModule ],
      declarations: [ HostComponent ],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HostComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});

