export default function SimpleTest() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f3f4f6',
      padding: '2rem'
    }}>
      <h1 style={{ 
        fontSize: '2rem', 
        fontWeight: 'bold',
        color: '#1f2937',
        marginBottom: '1rem'
      }}>
        CSS Test - Inline Styles
      </h1>
      <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        marginBottom: '1rem'
      }}>
        <p>This uses inline styles and should always work.</p>
      </div>
      
      <div className="bg-blue-500 text-white p-4 rounded-lg mb-4">
        <p>This uses Tailwind classes. If you see blue background and white text, Tailwind is working!</p>
      </div>
      
      <div className="bg-red-500 text-white p-4 rounded-lg mb-4">
        <p>This should be red with white text if Tailwind is working.</p>
      </div>
      
      <div className="bg-green-500 text-white p-4 rounded-lg">
        <p>This should be green with white text if Tailwind is working.</p>
      </div>
    </div>
  )
}