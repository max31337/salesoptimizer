# System Architecture

## 🏗️ High-Level System Architecture

```mermaid
graph TB
    subgraph "PRESENTATION LAYER"
        AP[Admin Panel<br/>• User Management<br/>• Audit Logs<br/>• System Settings<br/>• User Invitations]
        MP[Manager Portal<br/>• Team Management<br/>• Analytics Dashboard<br/>• Goal Setting<br/>• Task Assignment<br/>• Push Notifications]
        SRD[Sales Rep Dashboard<br/>• Opportunities<br/>• Customer Info<br/>• Interactions<br/>• Assigned Tasks<br/>• CSV Import<br/>• Push Notifications]
        PWA[PWA Features<br/>• Service Worker<br/>• Push Notifications<br/>• Offline Cache<br/>• Background Sync]
    end
    
    subgraph "APPLICATION LAYER"
        US[User Service<br/>• Authentication<br/>• RBAC<br/>• Multi-tenant<br/>• Session Mgmt]
        AS[Analytics Service<br/>• ML Predictions<br/>• Reporting<br/>• Data Pipeline<br/>• Success Probability]
        SS[Sales Service<br/>• Opportunity Mgmt<br/>• Customer Mgmt<br/>• Interaction Tracking<br/>• Pipeline Analysis]
        TS[Task Service<br/>• Task Assignment<br/>• Collaborative Tasks<br/>• Private Tasks<br/>• Task Notifications]
        NS[Notification Service<br/>• Push Notifications<br/>• Email Alerts<br/>• Task Reminders<br/>• Real-time Updates]
    end
    
    subgraph "DOMAIN LAYER (DDD)"
        OD[Organization Domain<br/>• Tenant<br/>• User<br/>• Role<br/>• Permission]
        SD[Sales Domain<br/>• Opportunity<br/>• Customer<br/>• Interaction<br/>• Pipeline]
        AD[Analytics Domain<br/>• Prediction Model<br/>• Historical Data<br/>• Success Rate<br/>• Trends]
        TD[Task Domain<br/>• Task<br/>• Assignment<br/>• Collaboration<br/>• Privacy Settings]
        ND[Notification Domain<br/>• Push Message<br/>• Subscription<br/>• Delivery Status<br/>• Preferences]
    end
    
    subgraph "INFRASTRUCTURE LAYER"
        DB[(PostgreSQL<br/>• Main Database<br/>• Multi-tenant<br/>• ACID Compliance)]
        CACHE[(Redis<br/>• Session Cache<br/>• Query Cache<br/>• Real-time Data)]
        MQ[Message Queue<br/>• Task Processing<br/>• Event Handling<br/>• Background Jobs)]
        ML[ML Data Store<br/>• Training Data<br/>• Model Storage<br/>• Feature Store]
        ES[External Services<br/>• Email Service<br/>• File Storage<br/>• CSV Parser<br/>• Push Service]
        WS[WebSocket Server<br/>• Real-time Updates<br/>• Task Notifications<br/>• Live Analytics]
        BW[Background Workers<br/>• Email Worker<br/>• Push Notification Worker<br/>• Analytics Worker<br/>• Data Sync Worker]
    end
    
    %% Connections
    AP --> US
    MP --> US
    MP --> TS
    MP --> NS
    SRD --> SS
    SRD --> TS
    SRD --> NS
    PWA --> NS
    
    US --> OD
    AS --> AD
    SS --> SD
    TS --> TD
    NS --> ND
    
    OD --> DB
    SD --> DB
    AD --> ML
    TD --> DB
    ND --> CACHE
    
    TS --> MQ
    NS --> MQ
    NS --> ES
    NS --> WS
    AS --> ML
    MQ --> BW
    BW --> ES
    BW --> DB
    
    %% Styling
    classDef presentation fill:#e3f2fd
    classDef application fill:#f3e5f5
    classDef domain fill:#e8f5e8
    classDef infrastructure fill:#fff3e0
    
    class AP,MP,SRD,PWA presentation
    class US,AS,SS,TS,NS application
    class OD,SD,AD,TD,ND domain
    class DB,CACHE,MQ,ML,ES,WS,BW infrastructure
```

## 🏛️ Domain-Driven Design Structure(Backend)

```
salesoptimizer/
├── domains/
│   ├── organization/
│   │   ├── entities/
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   └── permission.py
│   │   ├── repositories/
│   │   │   ├── tenant_repository_interface.py
│   │   │   └── user_repository_interface.py
│   │   ├── services/
│   │   │   ├── tenant_service.py
│   │   │   └── user_management_service.py
│   │   └── value_objects/
│   │       ├── tenant_id.py
│   │       └── user_role.py
│   ├── sales/
│   │   ├── entities/
│   │   │   ├── opportunity.py
│   │   │   ├── customer.py
│   │   │   └── interaction.py
│   │   ├── repositories/
│   │   │   ├── opportunity_repository_interface.py
│   │   │   └── customer_repository_interface.py
│   │   ├── services/
│   │   │   ├── opportunity_service.py
│   │   │   └── pipeline_service.py
│   │   └── value_objects/
│   │       ├── opportunity_stage.py
│   │       └── deal_value.py
│   ├── analytics/
│   │   ├── entities/
│   │   │   ├── prediction_model.py
│   │   │   └── historical_data.py
│   │   ├── repositories/
│   │   │   └── prediction_repository_interface.py
│   │   ├── services/
│   │   │   ├── prediction_engine.py
│   │   │   └── analytics_service.py
│   │   └── value_objects/
│   │       ├── success_probability.py
│   │       └── prediction_features.py
│   ├── tasks/
│   │   ├── entities/
│   │   │   ├── task.py
│   │   │   └── task_assignment.py
│   │   ├── repositories/
│   │   │   └── task_repository_interface.py
│   │   ├── services/
│   │   │   └── task_management_service.py
│   │   └── value_objects/
│   │       ├── task_priority.py
│   │       └── task_status.py
│   └── notifications/
│       ├── entities/
│       │   ├── push_notification.py
│       │   └── notification_subscription.py
│       ├── repositories/
│       │   └── notification_repository_interface.py
│       ├── services/
│       │   └── notification_service.py
│       └── value_objects/
│           ├── notification_type.py
│           └── delivery_status.py
├── application/
│   ├── services/
│   │   ├── authentication_service.py
│   │   ├── opportunity_application_service.py
│   │   ├── task_application_service.py
│   │   └── analytics_application_service.py
│   ├── handlers/
│   │   ├── create_opportunity_handler.py
│   │   ├── assign_task_handler.py
│   │   └── predict_outcome_handler.py
│   └── dtos/
│       ├── create_opportunity_dto.py
│       ├── assign_task_dto.py
│       └── predict_outcome_dto.py
├── infrastructure/
│   ├── persistence/
│   │   ├── sqlalchemy/
│   │   │   ├── database.py
│   │   │   ├── tenant_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── opportunity_repository.py
│   │   │   └── task_repository.py
│   │   └── mappers/
│   │       ├── tenant_mapper.py
│   │       ├── user_mapper.py
│   │       ├── opportunity_mapper.py
│   │       └── task_mapper.py
│   ├── messaging/
│   │   ├── events/
│   │   │   ├── task_assigned_event.py
│   │   │   └── opportunity_created_event.py
│   │   ├── subscribers/
│   │   │   ├── task_event_subscriber.py
│   │   │   └── notification_subscriber.py
│   │   └── publishers/
│   │       ├── kafka_publisher.py
│   │       └── in_memory_event_bus.py
│   ├── auth/
│   │   ├── jwt_provider.py
│   │   └── auth_middleware.py
├── interfaces/
│   ├── http/
│   │   ├── controllers/
│   │   │   ├── opportunity_controller.py
│   │   │   ├── task_controller.py
│   │   │   ├── auth_controller.py
│   │   │   └── analytics_controller.py
│   │   └── routes/
│   │       ├── opportunity_routes.py
│   │       ├── task_routes.py
│   │       ├── auth_routes.py
│   │       └── analytics_routes.py
│   ├── graphql/
│   │   ├── resolvers/
│   │   ├── schemas/
│   │   └── context.py
│   └── cli/
│       ├── seed.py
│       └── migrate.py
├── shared/
│   ├── kernel/
│   │   ├── base_entity.py
│   │   ├── domain_event.py
│   │   ├── entity_id.py
│   │   ├── result.py
│   │   └── guard.py
│   └── utils/
│       ├── date_utils.py
│       ├── logger.py
│       └── uuid_generator.py
├── config/
│   ├── settings.py
│   ├── database.py
│   └── env.py
└── main.py