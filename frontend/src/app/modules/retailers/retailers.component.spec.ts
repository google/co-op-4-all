import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RetailersComponent } from './retailers.component';

describe('RetailersComponent', () => {
  let component: RetailersComponent;
  let fixture: ComponentFixture<RetailersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RetailersComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RetailersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
