import { apiClient } from '@/lib/api'

export interface SLAAlert {
  id: string
  alert_type: 'warning' | 'critical'
  title: string
  message: string
  metric_type: string
  current_value: number
  threshold_value: number
  triggered_at: string
  acknowledged: boolean
  acknowledged_at: string | null
  acknowledged_by: string | null
}

export interface SLAMetric {
  id: string
  metric_type: string
  value: number
  status: 'healthy' | 'warning' | 'critical'
  unit: string
  threshold_warning: number
  threshold_critical: number
  measured_at: string
  additional_data?: Record<string, any>
}

export interface SLASystemHealth {
  overall_status: 'healthy' | 'warning' | 'critical'
  total_metrics: number
  healthy_metrics: number
  warning_metrics: number
  critical_metrics: number
  active_alerts: number
  unacknowledged_alerts: number
  last_check: string
  metrics_summary: {
    cpu_usage: number
    memory_usage: number
    disk_usage: number
    database_response_time: number
    active_users: number
    database_connections: number
  }
}

export interface SLAReport {
  id: string
  report_type: string
  overall_status: 'healthy' | 'warning' | 'critical'
  generated_at: string
  summary: string
  recommendations: string[]
  critical_metrics_count: number
  warning_metrics_count: number
  healthy_metrics_count: number
  total_metrics_count: number
  metrics_snapshot: Record<string, any>
  additional_data?: Record<string, any>
}

export interface AcknowledgeResponse {
  success: boolean
  message: string
  acknowledged_by: string
  acknowledged_at: string
}

class SLAService {
  private readonly basePath = '/admin/sla'

  async getSystemHealth(): Promise<SLASystemHealth> {
    return apiClient.get<SLASystemHealth>(`${this.basePath}/health`)
  }

  async getSystemHealthReport(): Promise<SLAReport> {
    return apiClient.get<SLAReport>(`${this.basePath}/report`)
  }

  async getCurrentAlerts(): Promise<SLAAlert[]> {
    return apiClient.get<SLAAlert[]>(`${this.basePath}/alerts`)
  }

  async getMetrics(metricTypes?: string[]): Promise<SLAMetric[]> {
    const params = metricTypes ? `?${metricTypes.map(type => `metric_types=${type}`).join('&')}` : ''
    return apiClient.get<SLAMetric[]>(`${this.basePath}/metrics${params}`)
  }

  async getMonitoringStatus(): Promise<{
    status: string
    service: string
    version: string
    features: string[]
    supported_metrics: string[]
  }> {
    return apiClient.get(`${this.basePath}/status`)
  }
  async acknowledgeAlert(alertId: string): Promise<AcknowledgeResponse> {
    return apiClient.post<AcknowledgeResponse>(`${this.basePath}/alerts/${alertId}/acknowledge`, {})
  }
}

export const slaService = new SLAService()
