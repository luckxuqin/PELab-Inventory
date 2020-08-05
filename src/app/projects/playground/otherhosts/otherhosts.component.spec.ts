import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SharedSpecModule } from '../../../shared/shared.module';

import { OtherhostsComponent } from './otherhosts.component';

describe('OtherhostsComponent', () => {
  let component: OtherhostsComponent;
  let fixture: ComponentFixture<OtherhostsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [ SharedSpecModule ],
      declarations: [ OtherhostsComponent ],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OtherhostsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});

