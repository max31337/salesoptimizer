"use client"

import { useState, useEffect } from "react"

export default function TestAvatarPage() {
  const [testImageUrl, setTestImageUrl] = useState<string>('')
  const [fetchResult, setFetchResult] = useState<string>('')
  const [imageLoaded, setImageLoaded] = useState<boolean>(false)
  const [imageError, setImageError] = useState<string>('')

  useEffect(() => {
    // Construct the test URL
    const url = `${process.env.NEXT_PUBLIC_API_URL}/uploads/profile_pictures/test.jpg`
    setTestImageUrl(url)
    console.log('🧪 Test image URL:', url)
    console.log('🧪 NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL)
  }, [])

  const testFetch = async () => {
    if (!testImageUrl) return
    
    try {
      console.log('🧪 Testing fetch to:', testImageUrl)
      const response = await fetch(testImageUrl)
      console.log('🧪 Fetch response:', response)
      console.log('🧪 Fetch status:', response.status)
      console.log('🧪 Fetch headers:', Array.from(response.headers.entries()))
      
      if (response.ok) {
        const blob = await response.blob()
        console.log('🧪 Blob size:', blob.size)
        console.log('🧪 Blob type:', blob.type)
        setFetchResult(`Success: ${response.status}, Size: ${blob.size}bytes, Type: ${blob.type}`)
      } else {
        const text = await response.text()
        setFetchResult(`Error: ${response.status} - ${text}`)
      }
    } catch (error) {
      console.error('🧪 Fetch error:', error)
      setFetchResult(`Fetch failed: ${error}`)
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Avatar Image Debug Test</h1>
      
      <div className="space-y-6">
        <div className="border p-4 rounded">
          <h2 className="text-lg font-semibold mb-2">Environment Variables</h2>
          <p><strong>NEXT_PUBLIC_API_URL:</strong> {process.env.NEXT_PUBLIC_API_URL}</p>
          <p><strong>Test URL:</strong> {testImageUrl}</p>
        </div>

        <div className="border p-4 rounded">
          <h2 className="text-lg font-semibold mb-2">Direct URL Test</h2>
          <p>Try accessing this URL directly in a new tab:</p>
          <a 
            href={testImageUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 underline break-all"
          >
            {testImageUrl}
          </a>
        </div>

        <div className="border p-4 rounded">
          <h2 className="text-lg font-semibold mb-2">Fetch Test</h2>
          <button 
            onClick={testFetch}
            className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
          >
            Test Fetch
          </button>
          <p><strong>Result:</strong> {fetchResult}</p>
        </div>

        <div className="border p-4 rounded">
          <h2 className="text-lg font-semibold mb-2">Image Element Test</h2>
          <div className="mb-4">
            <img 
              src={testImageUrl}
              alt="Test image"
              className="w-20 h-20 object-cover rounded border"
              onLoad={() => {
                console.log('🧪 Image loaded successfully')
                setImageLoaded(true)
                setImageError('')
              }}
              onError={(e) => {
                console.error('🧪 Image failed to load:', e)
                setImageLoaded(false)
                setImageError('Failed to load')
              }}
            />
          </div>
          <p><strong>Image Loaded:</strong> {imageLoaded ? 'Yes' : 'No'}</p>
          <p><strong>Image Error:</strong> {imageError}</p>
        </div>

        <div className="border p-4 rounded">
          <h2 className="text-lg font-semibold mb-2">Browser DevTools</h2>
          <p>Open browser DevTools (F12) and check:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Console tab for any JavaScript errors</li>
            <li>Network tab to see the actual request and response</li>
            <li>Check if CORS errors appear in console</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
