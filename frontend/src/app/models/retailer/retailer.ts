export interface Retailer {
    name: string;
    created_at?: string;
    bq_ga_table: string;
    time_zone: string;
    currency: string
    coop_max_backfill: number;
    is_active: boolean;
    modified_at?: string;
    bq_updated_at?: string
}