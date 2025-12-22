import { useState, useEffect } from 'react'
import './App.css'

import { API_BASE_URL } from './config'

const backgroundThemes = {
  'purple-blue': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'pink-orange': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'blue-cyan': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'green-turquoise': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'red-orange': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  'dark-purple': 'linear-gradient(135deg, #2d1b4e 0%, #11998e 100%)',
  'sunset': 'linear-gradient(135deg, #fa8bff 0%, #2bd2ff 0%, #2bff88 100%)',
  'ocean': 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)'
}

const headerThemes = {
  'red-pink': 'linear-gradient(135deg, #FF6B6B 0%, #FF5252 100%)',
  'purple': 'linear-gradient(135deg, #9D50BB 0%, #6E48AA 100%)',
  'blue': 'linear-gradient(135deg, #4A90E2 0%, #357ABD 100%)',
  'green': 'linear-gradient(135deg, #56AB2F 0%, #A8E063 100%)',
  'orange': 'linear-gradient(135deg, #F09819 0%, #EDDE5D 100%)',
  'teal': 'linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%)',
  'pink': 'linear-gradient(135deg, #F093FB 0%, #F5576C 100%)',
  'indigo': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
}

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [catDetection, setCatDetection] = useState(null)
  const [skipDetection, setSkipDetection] = useState(false)
  const [breedInfo, setBreedInfo] = useState(null)
  const [loadingInfo, setLoadingInfo] = useState(false)
  const [catAnalysis, setCatAnalysis] = useState(null)
  const [catAnalysisError, setCatAnalysisError] = useState(null)
  const [backgroundColor, setBackgroundColor] = useState('purple-blue')
  const [headerColor, setHeaderColor] = useState('red-pink')
  const [isDarkMode, setIsDarkMode] = useState(true)
  const [isDragging, setIsDragging] = useState(false)
  const [entropy, setEntropy] = useState(null)
  const [isWildCat, setIsWildCat] = useState(false)
  const [wildCatInfo, setWildCatInfo] = useState(null)
  const [uncertaintyThreshold, setUncertaintyThreshold] = useState(0.9)

  const processFile = (file) => {
    if (file) {
      setSelectedFile(file)
      setPredictions(null)
      setError(null)
      setCatDetection(null)

      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.onerror = () => {
        setError('Dosya okunamadı. Lütfen geçerli bir görsel dosyası seçin.')
      }
      reader.readAsDataURL(file)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      processFile(file)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      processFile(files[0])
    }
  }

  const handlePredict = async () => {
    if (!selectedFile) {
      setError('Lütfen bir fotoğraf seçin')
      return
    }

    setLoading(true)
    setError(null)
    setPredictions(null)
    setCatDetection(null)

    try {
      const formData = new FormData()
      formData.append('image', selectedFile)
      formData.append('skip_detection', skipDetection.toString())
      formData.append('uncertainty_threshold', uncertaintyThreshold.toString())

      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Tahmin yapılamadı')
      }

      setPredictions(data.predictions)
      setCatDetection(data.cat_detection)
      setEntropy(data.entropy)
      setIsWildCat(data.is_wild_cat)
      setWildCatInfo(data.wild_cat_info)

      // Set cat analysis if available
      if (data.cat_analysis) {
        setCatAnalysis(data.cat_analysis)
        setCatAnalysisError(null)
      } else if (data.cat_analysis_error) {
        setCatAnalysis(null)
        setCatAnalysisError(data.cat_analysis_error)
      } else {
        setCatAnalysis(null)
        setCatAnalysisError(null)
      }

      // Get breed info from Gemini AI for top prediction (optional feature)
      if (data.predictions && data.predictions.length > 0) {
        // Try to fetch breed info, but don't block if it fails
        fetchBreedInfo(data.predictions[0].breed).catch(err => {
          console.warn('Breed info fetch failed (optional feature):', err)
        })
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchBreedInfo = async (breedName) => {
    setLoadingInfo(true)
    setBreedInfo(null)

    try {
      const response = await fetch(`${API_BASE_URL}/breed-info`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ breed: breedName }),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setBreedInfo(data.info)
      } else {
        // Statik veritabanında bilgi yoksa sessizce geç (hata gösterme)
        console.log('Bilgi bulunamadı (statik veritabanında henüz eklenmemiş olabilir)')
      }
    } catch (err) {
      console.log('Breed info fetch error (optional feature):', err)
    } finally {
      setLoadingInfo(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreview(null)
    setPredictions(null)
    setError(null)
    setCatDetection(null)
    setBreedInfo(null)
    setCatAnalysis(null)
    setCatAnalysisError(null)
    setEntropy(null)
    setIsWildCat(false)
    setWildCatInfo(null)
  }

  const handleBackgroundChange = (theme) => {
    setBackgroundColor(theme)
    document.body.style.background = backgroundThemes[theme]
  }

  const handleHeaderChange = (theme) => {
    setHeaderColor(theme)
  }

  const handleThemeToggle = () => {
    setIsDarkMode(!isDarkMode)
    document.documentElement.setAttribute('data-theme', !isDarkMode ? 'dark' : 'light')
  }

  const parseMarkdown = (text) => {
    // **text** formatını <strong>text</strong> olarak değiştir
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  }

  const renderTextWithMarkdown = (text) => {
    const parsed = parseMarkdown(text)
    return <span dangerouslySetInnerHTML={{ __html: parsed }} />
  }

  // Set initial background on mount
  useEffect(() => {
    document.body.style.background = backgroundThemes[backgroundColor]
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light')
  }, [backgroundColor, isDarkMode])

  return (
    <div className="app">
      <div className="container">
        <header className="header" style={{ background: headerThemes[headerColor] }}>
          <button
            className="theme-toggle-btn header-toggle"
            onClick={handleThemeToggle}
            title={isDarkMode ? 'Açık Tema' : 'Koyu Tema'}
          >
            {isDarkMode ? '🌙' : '☀️'}
          </button>
          <div className="header-content">
            <div className="header-left">
              <div>
                <h1>🐱 Kedi Cinsi Tahmin Sistemi</h1>
                <p>Fotoğraf yükleyin ve "Tahmin Et" butonuna tıklayın</p>
              </div>
            </div>
            <div className="theme-selectors">
              <div className="theme-row">
                <div className="theme-selector">
                  <span className="theme-label">🎨 Arka Plan:</span>
                  <div className="theme-buttons">
                    {Object.keys(backgroundThemes).map((theme) => (
                      <button
                        key={theme}
                        className={`theme-btn ${backgroundColor === theme ? 'active' : ''}`}
                        onClick={() => handleBackgroundChange(theme)}
                        title={theme.replace('-', ' ')}
                        style={{
                          background: backgroundThemes[theme]
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <div className="theme-selector">
                <span className="theme-label">🎨 Header:</span>
                <div className="theme-buttons">
                  {Object.keys(headerThemes).map((theme) => (
                    <button
                      key={theme}
                      className={`theme-btn ${headerColor === theme ? 'active' : ''}`}
                      onClick={() => handleHeaderChange(theme)}
                      title={theme.replace('-', ' ')}
                      style={{
                        background: headerThemes[theme]
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="main-content">
          <div className="upload-section">
            <div
              className={`upload-box ${isDragging ? 'drag-over' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {preview ? (
                <div className="image-preview">
                  <img src={preview} alt="Preview" />
                  <button className="btn-remove" onClick={handleReset}>
                    <span>×</span>
                    <span>Kaldır</span>
                  </button>
                </div>
              ) : (
                <label className="upload-label">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="file-input"
                  />
                  <div className="upload-placeholder">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="17 8 12 3 7 8" />
                      <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                    <p>Fotoğraf Yükle</p>
                    <span>Tüm görsel formatları desteklenir</span>
                    <span style={{ marginTop: '5px', fontSize: '0.8rem', opacity: 0.6 }}>
                      JPG, PNG, WEBP, BMP, GIF, TIFF vb.
                    </span>
                    <span style={{ marginTop: '10px', fontSize: '0.85rem', opacity: 0.7 }}>
                      veya buraya sürükleyip bırakın
                    </span>
                  </div>
                </label>
              )}
            </div>

            <div className="controls">
              <div className="threshold-control" title="Daha düşük değerler 'Vahşi Kedi' uyarısını daha kolay tetikler. (Önerilen: 0.9)">
                <label className="threshold-label">
                  <span>Hassasiyet: {uncertaintyThreshold}</span>
                  <span className="threshold-tooltip">ℹ️</span>
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="2.0"
                  step="0.1"
                  value={uncertaintyThreshold}
                  onChange={(e) => setUncertaintyThreshold(parseFloat(e.target.value))}
                  className="threshold-slider"
                  style={{ '--accent-color': headerThemes[headerColor].split(',')[1].trim() }}
                />
              </div>
              <button
                className="btn-predict"
                onClick={handlePredict}
                disabled={!selectedFile || loading}
                style={{
                  background: headerThemes[headerColor]
                }}
              >
                {loading ? '⏳ Tahmin Yapılıyor...' : '🎯 Tahmin Et'}
              </button>
            </div>
          </div>

          <div className="results-section">
            {error && (
              <div className="error-box">
                <span className="error-icon">⚠️</span>
                <p>{error}</p>
              </div>
            )}

            {catDetection && (
              <div className={`detection-box ${catDetection.detected ? 'success' : 'warning'}`}>
                <span>{catDetection.detected ? '✅' : '❌'}</span>
                <div>
                  <p><strong>Kedi Tespiti:</strong> {catDetection.message}</p>
                  {catDetection.detected && (
                    <p>Güven: %{catDetection.confidence}</p>
                  )}
                </div>
              </div>
            )}

            {wildCatInfo && isWildCat && (
              <div className="wild-cat-alert" style={{
                background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)',
                padding: '40px',
                borderRadius: '20px',
                textAlign: 'center',
                boxShadow: '0 10px 40px rgba(255, 107, 107, 0.3)',
                marginTop: '20px'
              }}>
                <h2 style={{
                  fontSize: '2.5rem',
                  marginBottom: '20px',
                  color: 'white',
                  textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
                }}>
                  🦁 Vahşi Kedi Tespit Edildi!
                </h2>
                <div style={{
                  maxWidth: '600px',
                  margin: '30px auto',
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '15px',
                  overflow: 'hidden',
                  boxShadow: '0 5px 20px rgba(0,0,0,0.3)'
                }}>
                  <img
                    src="/wild-cat.gif"
                    alt="Vahşi Kedi"
                    style={{
                      width: '100%',
                      display: 'block',
                      maxHeight: '400px',
                      objectFit: 'cover'
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none'
                      e.target.parentElement.innerHTML = '<div style="padding: 60px; color: white; font-size: 4rem;">🦁🐆🐅</div>'
                    }}
                  />
                </div>
                <p style={{
                  fontSize: '1.3rem',
                  color: 'white',
                  marginTop: '20px',
                  lineHeight: '1.8'
                }}>
                  Bu görseldeki hayvan <strong>vahşi bir kedi türü</strong>dür.
                  <br />
                  Sistemimiz yalnızca <strong>59 ev kedisi ırkı</strong> için eğitilmiştir.
                </p>
              </div>
            )}

            {wildCatInfo && !isWildCat && (
              <div className={`detection-box success`}>
                <span>✅</span>
                <div>
                  <p><strong>Görsel Analiz:</strong></p>
                  <p style={{ fontSize: '0.95rem', marginTop: '8px' }}>{wildCatInfo.explanation}</p>
                  {entropy && (
                    <p style={{ fontSize: '0.85rem', marginTop: '8px', opacity: 0.8 }}>
                      Entropi: {entropy} | Eşik: {wildCatInfo.threshold}
                    </p>
                  )}
                </div>
              </div>
            )}

            {predictions && !isWildCat && (
              <div className="predictions-box">
                <h2>🎯 Tahmin Sonuçları</h2>

                <div className="top-prediction">
                  <div className="prediction-header">
                    <h3>{predictions[0].breed}</h3>
                    <span className="confidence-badge">
                      %{predictions[0].confidence}
                    </span>
                  </div>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${predictions[0].confidence}%` }}
                    />
                  </div>
                </div>

                <div className="other-predictions">
                  <h4>Diğer Olası Cinler:</h4>
                  {predictions.slice(1, 3).map((pred, index) => (
                    <div key={index} className="prediction-item">
                      <span className="prediction-breed">{pred.breed}</span>
                      <span className="prediction-confidence">%{pred.confidence}</span>
                      <div className="prediction-bar">
                        <div
                          className="prediction-fill"
                          style={{ width: `${pred.confidence}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

              </div>
            )}

            {!predictions && !error && !loading && (
              <div className="placeholder-box">
                <p>👆 Bir fotoğraf yükleyin ve "Tahmin Et" butonuna tıklayın</p>
              </div>
            )}
          </div>

          {/* AI Analysis Sections - Full width outside grid */}
          {predictions && !isWildCat && (
            <div className="ai-sections-full-width">
              {/* Cat Image Analysis (Gemini Vision) */}
              <div className="cat-analysis-container">
                {catAnalysis && (
                  <div className="cat-analysis-box">
                    <h3>🔍 Fotoğraf Analizi</h3>
                    <div className="breed-info-content">
                      {catAnalysis.split('\n').map((paragraph, index) => (
                        paragraph.trim() && (
                          <p key={index}>{renderTextWithMarkdown(paragraph.trim())}</p>
                        )
                      ))}
                    </div>
                  </div>
                )}

                {catAnalysisError && !catAnalysis && (
                  <div className="breed-info-box" style={{ borderLeftColor: '#ff9800', background: '#1E1E1E' }}>
                    <h3>⚠️ Görsel Analiz</h3>
                    <div className="breed-info-content">
                      <p>{catAnalysisError}</p>
                      <p style={{ fontSize: '0.85rem', opacity: 0.8, marginTop: '10px' }}>
                        💡 Not: Kedi cinsi tahmin özelliği normal çalışmaya devam ediyor. Sadece görsel analiz (yaş, sağlık durumu) şu anda kullanılamıyor.
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Breed Info - Using Static Database (FREE) */}
              <div className="breed-info-container">
                {loadingInfo && (
                  <div className="breed-info-loading">
                    <p>📚 {predictions[0].breed} hakkında bilgi yükleniyor...</p>
                  </div>
                )}

                {breedInfo && !loadingInfo && (
                  <div className="breed-info-box">
                    <h3>📖 {predictions[0].breed} Hakkında</h3>
                    <div className="breed-info-content">
                      {breedInfo.split('\n').map((paragraph, index) => (
                        paragraph.trim() && (
                          <p key={index}>{renderTextWithMarkdown(paragraph.trim())}</p>
                        )
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <footer className="footer">
          <p>🚀 Bu proje Tekirdağ Namık Kemal Üniveristesi öğrencileri tarafından yapılmıştır.</p>
        </footer>
      </div>
    </div>
  )
}

export default App
