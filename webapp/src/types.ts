export interface WorstModel {
  name: string;
  field: string;
  header: string;
  visible: boolean;
  type: string;
  svg_path: string;
}

export interface Model {
  id: string;
  parent_type: string;
  parent_id: string;
  name: string;
  owned_by: string;
  permissions: string;
  tags: string[];
  created_at: string;
  created_by: string;
  updated_at: string;
  updated_by: string;
  attachments: string[];
  in_overview: boolean;
  type: string;
  header: string;
}
