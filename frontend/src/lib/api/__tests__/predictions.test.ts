import { describe, it, expect, vi, beforeEach } from "vitest"

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

const API_URL = "http://localhost:8000"

beforeEach(() => {
  mockFetch.mockReset()
})

async function predictSymptoms(
  input: {
    symptoms: string[]
    age?: number | null
    gender?: string | null
    existing_conditions?: string[]
    symptom_duration?: string
    pain_level?: number | null
  },
  token?: string
) {
  const response = await fetch(`${API_URL}/api/v1/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || "Prediction request failed")
  }
  return response.json()
}

async function fetchUserReports(userId: string, token?: string) {
  const response = await fetch(`${API_URL}/api/v1/reports/${userId}`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
  if (!response.ok) {
    if (response.status === 404) return null
    throw new Error("Failed to fetch reports")
  }
  return response.json()
}

async function fetchDoctors(
  params?: {
    q?: string
    specialty?: string
    location?: string
    sort_by?: string
    sort_order?: string
    limit?: number
  },
  token?: string
) {
  const searchParams = new URLSearchParams()
  if (params?.q) searchParams.set("q", params.q)
  if (params?.specialty) searchParams.set("specialty", params.specialty)
  if (params?.location) searchParams.set("location", params.location)
  if (params?.sort_by) searchParams.set("sort_by", params.sort_by)
  if (params?.sort_order) searchParams.set("sort_order", params.sort_order)
  if (params?.limit) searchParams.set("limit", String(params.limit))
  const response = await fetch(
    `${API_URL}/api/v1/doctors?${searchParams.toString()}`,
    { headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) } }
  )
  if (!response.ok) throw new Error("Failed to fetch doctors")
  return response.json()
}

async function fetchSymptoms(
  params?: { q?: string; category?: string; limit?: number },
  token?: string
) {
  const searchParams = new URLSearchParams()
  if (params?.q) searchParams.set("q", params.q)
  if (params?.category) searchParams.set("category", params.category)
  if (params?.limit) searchParams.set("limit", String(params.limit))
  const response = await fetch(
    `${API_URL}/api/v1/symptoms/search?${searchParams.toString()}`,
    { headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) } }
  )
  if (!response.ok) throw new Error("Failed to fetch symptoms")
  return response.json()
}

describe("predictSymptoms", () => {
  it("sends POST request with correct body", async () => {
    const mockResponse = { primary_prediction: "Influenza", confidence: 85.5 }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const result = await predictSymptoms({
      symptoms: ["fever", "cough"],
      age: 30,
    })

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/api/v1/predict`,
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
        body: JSON.stringify({ symptoms: ["fever", "cough"], age: 30 }),
      })
    )
    expect(result).toEqual(mockResponse)
  })

  it("includes auth token in headers", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    })

    await predictSymptoms({ symptoms: [] }, "test-token")

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      })
    )
  })

  it("throws on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      text: async () => "Bad request",
    })

    await expect(
      predictSymptoms({ symptoms: ["fever"] })
    ).rejects.toThrow("Bad request")
  })
})

describe("fetchUserReports", () => {
  it("returns null on 404", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 404 })

    const result = await fetchUserReports("user-1")
    expect(result).toBeNull()
  })

  it("throws on non-404 errors", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 500 })

    await expect(fetchUserReports("user-1")).rejects.toThrow(
      "Failed to fetch reports"
    )
  })

  it("returns data on success", async () => {
    const data = { total_predictions: 5 }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => data,
    })

    const result = await fetchUserReports("user-1")
    expect(result).toEqual(data)
  })
})

describe("fetchDoctors", () => {
  it("sends query params", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({ results: [] }) })

    await fetchDoctors({ q: "heart", specialty: "Cardiologist", limit: 10 })

    const url = mockFetch.mock.calls[0][0]
    expect(url).toContain("q=heart")
    expect(url).toContain("specialty=Cardiologist")
    expect(url).toContain("limit=10")
  })

  it("throws on error", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 500 })

    await expect(fetchDoctors()).rejects.toThrow("Failed to fetch doctors")
  })
})

describe("fetchSymptoms", () => {
  it("sends search params", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({ results: [] }) })

    await fetchSymptoms({ q: "head", category: "Neurological" })

    const url = mockFetch.mock.calls[0][0]
    expect(url).toContain("q=head")
    expect(url).toContain("category=Neurological")
  })
})
