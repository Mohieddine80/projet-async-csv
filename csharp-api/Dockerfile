FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copier le fichier .csproj et restaurer les dépendances
COPY *.csproj ./
RUN dotnet restore

# Copier tout le reste et builder
COPY . .
RUN dotnet publish -c Release -o /app/publish

# Image finale
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .

EXPOSE 5001

ENTRYPOINT ["dotnet", "csharp-api.dll"]