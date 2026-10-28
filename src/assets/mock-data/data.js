// Mock data for the Ellio MVP Frontend
// This demonstrates the data structures that would be used in a real implementation

export const mockProject = {
  id: 'proj-001',
  name: 'Summer Campaign Video',
  brief: {
    objective: 'Create an engaging promotional video for our new summer product line',
    audience: 'Young adults aged 18-35 interested in outdoor activities',
    tone: 'energetic and inspiring',
    storyBeats: [
      'Product introduction in natural setting',
      'Close-ups of product features',
      'People enjoying the product in various activities',
      'Group shot showing community and enjoyment',
      'Brand logo and call to action'
    ],
    deliverables: {
      web: true,
      social: true,
      broadcast: false,
      archive: true
    },
    visualReferences: [
      'https://example.com/ref1.jpg',
      'https://example.com/ref2.jpg'
    ],
    audioReferences: [
      'https://example.com/track1.mp3',
      'https://example.com/track2.mp3'
    ]
  },
  createdAt: '2026-09-20T10:30:00Z',
  updatedAt: '2026-09-25T15:00:00Z'
}

export const mockMediaLibrary = [
  {
    id: 'asset-001',
    name: 'opening_shot.mp4',
    type: 'video',
    original: { ready: true, progress: 100 },
    proxy: { ready: true, progress: 100 },
    transcript: { ready: true, progress: 100 },
    analysis: { ready: true, progress: 100 },
    status: 'ready',
    thumbnail: 'https://via.placeholder.com/320x180?opening_shot',
    duration: '00:08:15',
    fileSize: '2.4 GB',
    createdAt: '2026-09-25T14:30:00Z'
  },
  {
    id: 'asset-002',
    name: 'interview_segment.mp4',
    type: 'video',
    original: { ready: true, progress: 100 },
    proxy: { ready: true, progress: 100 },
    transcript: { ready: true, progress: 100 },
    analysis: { ready: true, progress: 100 },
    status: 'ready',
    thumbnail: 'https://via.placeholder.com/320x180?interview',
    duration: '00:04:22',
    fileSize: '1.8 GB',
    createdAt: '2026-09-25T14:25:00Z'
  },
  {
    id: 'asset-003',
    name: 'b-roll_nature.mp4',
    type: 'video',
    original: { ready: true, progress: 100 },
    proxy: { ready: true, progress: 100 },
    transcript: { ready: true, progress: 100 },
    analysis: { ready: true, progress: 100 },
    status: 'ready',
    thumbnail: 'https://via.placeholder.com/320x180?b-roll',
    duration: '00:12:40',
    fileSize: '3.2 GB',
    createdAt: '2026-09-25T14:20:00Z'
  }
]

export const mockSelectsReel = {
  selections: [
    {
      inPoint: 12.5,
      outPoint: 18.3,
      assetId: 'asset-001',
      metadata: {
        shotType: 'medium close-up',
        emotion: 'hopeful',
        storyBeat: 'product introduction',
        aiRationale: 'Strong eye contact and natural lighting'
      }
    },
    {
      inPoint: 5.2,
      outPoint: 9.8,
      assetId: 'asset-002',
      metadata: {
        shotType: 'two-shot',
        emotion: 'engaged',
        storyBeat: 'feature explanation',
        aiRationale: 'Good chemistry between subjects'
      }
    },
    {
      inPoint: 22.1,
      outPoint: 27.6,
      assetId: 'asset-003',
      metadata: {
        shotType: 'wide establishing',
        emotion: 'peaceful',
        storyBeat: 'product in environment',
        aiRationale: 'Beautiful natural lighting and composition'
      }
    }
  ],
  playhead: 15.2,
  isPlaying: false,
  volume: 0.8
}

export const mockTimeline = {
  tracks: [
    {
      id: 'track-v1',
      type: 'video',
      name: 'Video Track 1',
      clips: [
        {
          id: 'clip-v1',
          assetId: 'asset-001',
          inPoint: 12.5,
          outPoint: 18.3,
          startTime: 0,
          endTime: 5.8
        },
        {
          id: 'clip-v2',
          assetId: 'asset-002',
          inPoint: 5.2,
          outPoint: 9.8,
          startTime: 5.8,
          endTime: 10.4
        }
      ]
    },
    {
      id: 'track-a1',
      type: 'audio',
      name: 'Audio Track 1',
      clips: [
        {
          id: 'clip-a1',
          assetId: 'asset-001',
          inPoint: 12.5,
          outPoint: 18.3,
          startTime: 0,
          endTime: 5.8,
          gain: 0.0
        }
      ]
    }
  ],
  playhead: 4.2,
  isPlaying: false,
  zoomLevel: 1.0,
  markers: [
    {
      id: 'marker-1',
      time: 5.8,
      type: 'in',
      label: 'First cut'
    },
    {
      id: 'marker-2',
      time: 10.4,
      type: 'out',
      label: 'End of sequence'
    }
  ]
}

export const mockAIState = {
  isGenerating: false,
  currentPrompt: 'Make this feel more energetic and upbeat',
  context: {
    type: 'range',
    assetId: 'asset-001',
    inPoint: 12.5,
    outPoint: 18.3,
    description: 'Opening product shot'
  },
  scope: ['Story', 'Composition', 'Motion'],
  preservation: 0.3, // More towards creative reinterpretation
  results: [
    {
      id: 'result-001',
      type: 'color-grading',
      description: 'Increased saturation and contrast',
      confidence: 0.85,
      generatedAt: '2026-09-25T15:15:00Z'
    },
    {
      id: 'result-002',
      type: 'music-suggestion',
      description: 'Upbeat electronic track with progressive build',
      confidence: 0.92,
      generatedAt: '2026-09-25T15:16:00Z'
    }
  ],
  selectedResult: null
}

export const mockNotifications = [
  {
    id: 'notif-001',
    type: 'success',
    title: 'Asset Import Complete',
    message: '3 assets imported and processed successfully',
    timeout: 5000
  },
  {
    id: 'notif-002',
    type: 'info',
    title: 'AI Analysis Complete',
    message: 'Scene analysis finished for selected range',
    progress: 100,
    timeout: 3000
  }
]