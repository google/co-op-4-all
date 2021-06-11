import { Filter } from './filter';
import { GoogleAdsDestination } from './google-ads-destination';
import { DV360Destination } from './dv360-destination';

export interface CoopConfiguration {
    name: string
    retailer_name: string
    attribution_window: number
    filters: Array<Filter>
    utm_campaigns: Array<string>
    destinations: Array<GoogleAdsDestination|DV360Destination>
    is_active: boolean
    created_at?: string
    modified_at?: string
}