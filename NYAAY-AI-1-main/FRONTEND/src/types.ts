export type DomainCategory = 'RTI' | 'CONSUMER' | 'TENANT' | 'WORKPLACE' | 'GENERAL_CIVIL' | 'RERA_PROPERTY';

export interface StatutorySection {
  act: string;
  section: string;
  title: string;
  statutoryQuote: string;
  plainExplanation: string;
  relevanceScore: number;
}

export interface EvidenceItem {
  id: string;
  title: string;
  description: string;
  category?: 'ALREADY PROVIDED' | 'RECOMMENDED' | 'SUPPORTING';
  isMandatory: boolean;
  evidentiaryWeight: 'CRITICAL' | 'HIGH' | 'SUPPORTING';
  checked: boolean;
  fileAttached?: string;
  notes?: string;
}

export interface AuthorityEscalation {
  tier: number;
  authorityName: string;
  timeframe: string;
  prerequisite: string;
  procedure: string;
}

export interface RelevantAuthorityInfo {
  designatedBody: string;
  officerTitle: string;
  jurisdictionLevel: string;
  statutoryTimeLimit: string;
  appealPeriod: string;
  filingFee: string;
  escalationPath: AuthorityEscalation[];
  officialPortalUrl?: string;
}

export interface ActionPlanStep {
  stepNumber: number;
  title: string;
  timeframe: string;
  description: string;
  actionType: 'FILING' | 'EVIDENCE_GATHERING' | 'FORMAL_NOTICE' | 'ESCALATION' | 'HEARING';
  status: 'pending' | 'in_progress' | 'completed';
  statutoryDeadlineNotice?: string;
}

export interface DocumentDraftData {
  documentRecommended: boolean;
  reasoning: string;
  documentType: string;
  title: string;
  actReference: string;
  suggestedFormNumber?: string;
  placeholders: Record<string, string>;
  templateBody: string;
  instructions: string[];
}

export interface FivePartCaseDossier {
  problemAndRights: {
    docketId: string;
    domain: DomainCategory;
    yourLegalProblem: string;
    whatTheLawSays: string;
    potentialRights: string[];
    missingInformation: string;
    criticalTakeaway: string;
  };
  evidenceRequired: {
    minimumEvidentiaryThreshold: string;
    items: EvidenceItem[];
    auditReadinessScore: number;
  };
  relevantAuthority: RelevantAuthorityInfo;
  actionPlan: {
    totalEstimatedDays: number;
    steps: ActionPlanStep[];
  };
  documentGeneration: DocumentDraftData;
}

export interface BareAct {
  id: string;
  actCode: string;
  title: string;
  year: number;
  actNumber: string;
  category: 'CIVIC_RIGHTS' | 'CONSUMER_COMMERCIAL' | 'PROPERTY_HOUSING' | 'CONSTITUTIONAL' | 'PENAL_PROCEDURAL' | 'ENVIRONMENTAL_LABOR';
  sectionCount: number;
  summary: string;
  keySections: string[];
}

export interface RetrievalMetrics {
  denseChromaScore: number;
  sparseBM25Score: number;
  rrfFusedScore: number;
  latencyMs: number;
  retrievedChunksCount: number;
  matchedActId: string;
  matchedActTitle: string;
}

export interface SavedCaseRecord {
  id: string;
  docketNumber: string;
  title: string;
  domain: DomainCategory;
  createdAt: string;
  status: 'ACTIVE' | 'RESOLVED' | 'DRAFTING';
  dossier: FivePartCaseDossier;
}
