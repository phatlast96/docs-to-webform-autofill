export interface AutofillResponse {
  form_field_count: number;
  llm_output: Record<string, string | boolean | null>;
  fill_result: { filled: string[]; skipped: string[] };
  input_tokens: number;
  output_tokens: number;
}
