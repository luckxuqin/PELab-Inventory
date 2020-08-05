import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SharedSpecModule } from '../../../../shared/shared.module';

import { UpdatevcfhostComponent } from './updatevcfhost.component';

describe('UpdatevcfhostComponent', () => {
  let component: UpdatevcfhostComponent;
  let fixture: ComponentFixture<UpdatevcfhostComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [ SharedSpecModule ],
      declarations: [ UpdatevcfhostComponent ],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UpdatevcfhostComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});

