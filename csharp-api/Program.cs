using MongoDB.Driver;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

// Configuration CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Configuration MongoDB
var mongoConnectionString = Environment.GetEnvironmentVariable("ConnectionStrings__MongoDb") 
    ?? "mongodb://mongodb:27017";
var mongoClient = new MongoClient(mongoConnectionString);
var database = mongoClient.GetDatabase("csvdb");
var collection = database.GetCollection<DataRecord>("records");

// Créer un index unique sur le champ Id pour éviter les doublons
var indexKeysDefinition = Builders<DataRecord>.IndexKeys.Ascending(x => x.RecordId);
var indexOptions = new CreateIndexOptions { Unique = true };
var indexModel = new CreateIndexModel<DataRecord>(indexKeysDefinition, indexOptions);
await collection.Indexes.CreateOneAsync(indexModel);

builder.Services.AddSingleton(collection);

var app = builder.Build();

app.UseCors("AllowAll");

// Endpoint de test
app.MapGet("/", () => new
{
    service = "C# API - CSV Data Handler",
    status = "running",
    version = "1.0",
    database = "MongoDB"
});

// Endpoint pour insérer des données
app.MapPost("/api/data/insert", async (JsonElement data, IMongoCollection<DataRecord> col) =>
{
    try
    {
        // Convertir JsonElement en dictionnaire
        var dataDict = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(data.GetRawText());
        
        if (dataDict == null || !dataDict.Any())
        {
            return Results.BadRequest(new { error = "Données vides" });
        }

        // Créer un ID unique basé sur les données (ou utiliser un champ spécifique)
        // Ici on utilise le premier champ comme identifiant unique
        var firstKey = dataDict.Keys.First();
        var recordId = dataDict[firstKey].ToString();

        var record = new DataRecord
        {
            RecordId = recordId,
            Data = dataDict.ToDictionary(
                kvp => kvp.Key,
                kvp => kvp.Value.ToString()
            ),
            CreatedAt = DateTime.UtcNow
        };

        try
        {
            // Tenter d'insérer
            await col.InsertOneAsync(record);
            
            return Results.Ok(new
            {
                inserted = true,
                message = "Donnée insérée avec succès",
                recordId = recordId
            });
        }
        catch (MongoWriteException ex) when (ex.WriteError.Category == ServerErrorCategory.DuplicateKey)
        {
            // Doublon détecté
            return Results.Ok(new
            {
                inserted = false,
                message = "Doublon détecté, ligne ignorée",
                recordId = recordId
            });
        }
    }
    catch (Exception ex)
    {
        return Results.Problem(
            detail: ex.Message,
            statusCode: 500
        );
    }
});

// Endpoint pour récupérer toutes les données
app.MapGet("/api/data/all", async (IMongoCollection<DataRecord> col) =>
{
    var records = await col.Find(_ => true).ToListAsync();
    return Results.Ok(new
    {
        count = records.Count,
        records = records
    });
});

// Endpoint pour compter les enregistrements
app.MapGet("/api/data/count", async (IMongoCollection<DataRecord> col) =>
{
    var count = await col.CountDocumentsAsync(_ => true);
    return Results.Ok(new { count = count });
});

// Endpoint pour supprimer toutes les données (utile pour les tests)
app.MapDelete("/api/data/clear", async (IMongoCollection<DataRecord> col) =>
{
    await col.DeleteManyAsync(_ => true);
    return Results.Ok(new { message = "Base de données vidée" });
});

app.Run();

// Modèle de données
public class DataRecord
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    [BsonElement("recordId")]
    public string RecordId { get; set; } = string.Empty;

    [BsonElement("data")]
    public Dictionary<string, string> Data { get; set; } = new();

    [BsonElement("createdAt")]
    public DateTime CreatedAt { get; set; }
}