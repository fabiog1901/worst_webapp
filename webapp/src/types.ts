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
  name: string;
  owned_by: string;
  tags: string[];
  created_at: string;
  created_by: string;
  updated_at: string;
  updaded_by: string;
  attachments: string[];
  visible: boolean;
  type: string;
  header: string;
}
