export class Retailer {
    name: string;
    createdAt: string;
    bqGaTable: string;
    bqDataSet: string;
    timezone: string;
    maxBackfill: number;
    active: boolean;

    constructor() {
        this.name = '';
        this.createdAt = '';
        this.bqGaTable = '';
        this.bqDataSet = '';
        this.timezone = '';
        this.maxBackfill = 3;
        this.active = true;
    }
}