import { useEffect, useState } from 'react';
import axios from 'axios';
import { Chart } from 'chart.js/auto';

function App() {
  const [series, setSeries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/dashboard')
      .then((response) => {
        setSeries(response.data.series || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!series.length) return;

    const canvas = document.getElementById('priceChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const datasets = series.map((item) => ({
      label: item.name,
      data: item.avg_price,
      borderColor: '#' + Math.floor(Math.random() * 16777215).toString(16),
      fill: false,
      tension: 0.2,
    }));

    const labels = series[0]?.dates || [];

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets,
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: true,
          },
        },
      },
    });

    return () => chart.destroy();
  }, [series]);

  return (
    <div style={{ padding: '24px', fontFamily: 'Arial' }}>
      <h1>Finance Dashboard</h1>
      {loading ? <p>Yükleniyor...</p> : <canvas id="priceChart" />}
    </div>
  );
}

export default App;
