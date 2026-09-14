const request = require("supertest");
const app = require("../app");

describe("Health Check", () => {
  test("GET /health should return 200", async () => {
    const response = await request(app).get("/health");

    expect(response.statusCode).toBe(200);
    expect(response.body.status).toBe("UP");
  });
});

describe("Tasks API", () => {
  test("GET /api/tasks should return tasks", async () => {
    const response = await request(app).get("/api/tasks");

    expect(response.statusCode).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
  });

  test("GET /api/tasks/1 should return a task", async () => {
    const response = await request(app).get("/api/tasks/1");

    expect(response.statusCode).toBe(200);
    expect(response.body.id).toBe(1);
  });

  test("GET /api/tasks/999 should return 404", async () => {
    const response = await request(app).get("/api/tasks/999");

    expect(response.statusCode).toBe(404);
    expect(response.body.error).toBe("Task not found");
  });

  test("POST /api/tasks should create a task", async () => {
    const response = await request(app)
      .post("/api/tasks")
      .send({
        title: "Learn Jenkins"
      });

    expect(response.statusCode).toBe(201);
    expect(response.body.title).toBe("Learn Jenkins");
    expect(response.body.completed).toBe(false);
  });

  test("POST /api/tasks without title should return 400", async () => {
    const response = await request(app)
      .post("/api/tasks")
      .send({});

    expect(response.statusCode).toBe(400);
    expect(response.body.error).toBe("Title is required");
  });

test("PUT /api/tasks/1 should update a task", async () => {
  const response = await request(app)
    .put("/api/tasks/1")
    .send({
      title: "Learn Advanced Jenkins",
      completed: true
    });

  expect(response.statusCode).toBe(200);
  expect(response.body.title).toBe("Learn Advanced Jenkins");
  expect(response.body.completed).toBe(true);
});

test("DELETE /api/tasks/2 should delete a task", async () => {
  const response = await request(app)
    .delete("/api/tasks/2");

  expect(response.statusCode).toBe(200);
  expect(response.body.id).toBe(2);
});
});