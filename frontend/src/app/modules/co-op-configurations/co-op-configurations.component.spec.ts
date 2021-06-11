import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CoOpConfigurationsComponent } from './co-op-configurations.component';

describe('CoOpConfigurationsComponent', () => {
  let component: CoOpConfigurationsComponent;
  let fixture: ComponentFixture<CoOpConfigurationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CoOpConfigurationsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CoOpConfigurationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
