export class Retailer {
    name: string;
    created_at: string;
    bq_ga_table: string;
    bq_dataset: string;
    time_zone: string;
    max_backfill: number;
    is_active: boolean;
    modified_at?: string;

    constructor() {
        this.name = '';
        this.created_at = '';
        this.bq_ga_table = '';
        this.bq_dataset = '';
        this.time_zone = '';
        this.max_backfill = 3;
        this.is_active = true;
        this.modified_at = '';
    }
}