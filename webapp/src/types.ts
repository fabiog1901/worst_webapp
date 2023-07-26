export interface AccountOverview {
  account_id: string;
  name: string;
  owned_by: string;
  status: string;
  due_date: string;
  tags: string[];
  created_at: string;
  created_by: string;
  updated_at: string;
  updaded_by: string;
  attachments: string[];
}

export interface Account {
  account_id: string;
  name: string;
  owned_by: string;
  status: string;
  due_date: string;
  tags: string[];
  text: string;
  created_at: string;
  created_by: string;
  updated_at: string;
  updaded_by: string;
  attachments: string[];
}

export interface OpportunityOverviewWithAccountName {
  account_id: string;
  opportunity_id: string;
  name: string;
  owned_by: string;
}

export interface ContactWithAccountName {
  account_id: string;
  account_name: string;
  contact_id: string;
  fname: string;
  lname: string;
  role_title: string;
  email: string;
  telephone_number: string;
  tags: string[];
  business_card: string;
  created_at: string;
  created_by: string;
  updated_at: string;
  updaded_by: string;
}
