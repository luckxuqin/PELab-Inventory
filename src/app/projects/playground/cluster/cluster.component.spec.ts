import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SharedSpecModule } from '../../../shared/shared.module';

import { ClusterComponent } from './cluster.component';

describe('ClusterComponent', () => {
  let component: ClusterComponent;
  let fixture: ComponentFixture<ClusterComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [ SharedSpecModule ],
      declarations: [ ClusterComponent ],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ClusterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});

