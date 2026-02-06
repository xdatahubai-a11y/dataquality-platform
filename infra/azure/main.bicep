// Azure Container Apps deployment for DataQuality Platform

param location string = resourceGroup().location
param environmentName string = 'dq-platform-env'
param apiImageName string = 'dqplatform/api:latest'
param dashboardImageName string = 'dqplatform/dashboard:latest'

resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
    }
  }
}

resource apiApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'dq-api'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8000
      }
    }
    template: {
      containers: [
        {
          name: 'api'
          image: apiImageName
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'DQ_DATABASE_URL', value: 'postgresql://dq:dqpass@postgres:5432/dataquality' }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
      }
    }
  }
}

resource dashboardApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'dq-dashboard'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 80
      }
    }
    template: {
      containers: [
        {
          name: 'dashboard'
          image: dashboardImageName
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}
