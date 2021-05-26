import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CoOpConfigurationFormComponent } from './co-op-configuration-form.component';

describe('CoOpConfigurationFormComponent', () => {
  let component: CoOpConfigurationFormComponent;
  let fixture: ComponentFixture<CoOpConfigurationFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CoOpConfigurationFormComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CoOpConfigurationFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
