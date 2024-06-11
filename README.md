# Pulumi Reference

This project contains a pulumi reference of the following:

* multi-project infra repos
* a pulumi Component
  * Code organization patterns within the component

## Application Design

```mermaid
graph LR
subgraph "Data Stack"
A[S3 Bucket]
end
subgraph "App Stack"
B[Lambda Function]
C[SQS Queue]
end
C -->|Event Source Mapping| B
B -->A
```
