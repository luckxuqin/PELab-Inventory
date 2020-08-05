import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SharedSpecModule } from '../../../shared/shared.module';

import { UpdateComponent } from './update.component';

describe('OtherhostsComponent', () => {
  let component: UpdateComponent;
  let fixture: ComponentFixture<UpdateComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [ SharedSpecModule ],
      declarations: [ UpdateComponent ],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UpdateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});

