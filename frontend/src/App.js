import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { FileDown, Link as LinkIcon, Info, Building2, ScrollText } from 'lucide-react';

function App() {
  const baseUrl = window.location.origin;
  const dynamicPdfUrl = `${process.env.REACT_APP_API_URL || ''}/api/latest-report`;
  
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [copied, setCopied] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const autoDownloadUrl = `${baseUrl}?download=true&pdfUrl=${encodeURIComponent(dynamicPdfUrl)}`;
    setQrCodeUrl(autoDownloadUrl);

    // Check if we should trigger download
    const urlParams = new URLSearchParams(window.location.search);
    const shouldDownload = urlParams.get('download') === 'true';
    const pdfUrl = urlParams.get('pdfUrl');

    if (shouldDownload && pdfUrl) {
      window.location.href = pdfUrl;
    }

    // Fetch last update time
    fetch(`${process.env.REACT_APP_API_URL || ''}/api/last-update`)
      .then(res => res.json())
      .then(data => {
        setLastUpdate(new Date(data.lastUpdate));
      })
      .catch(console.error);
  }, []);

  const handleCopyUrl = () => {
    navigator.clipboard.writeText(qrCodeUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-6" dir="rtl">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="flex flex-col items-center text-center mb-8 border-b border-gray-200 pb-6">
            <div className="flex items-center gap-3 mb-2">
              <Building2 className="w-10 h-10 text-emerald-600" />
              <ScrollText className="w-10 h-10 text-emerald-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">وزارة الصحة في الجمهورية العربية السورية</h1>
            <h2 className="text-xl text-emerald-700 font-semibold">بوابة الأبحاث الطبية</h2>
            {lastUpdate && (
              <p className="text-sm text-gray-600 mt-2">
                آخر تحديث: {lastUpdate.toLocaleDateString('ar-SY')}
              </p>
            )}
          </div>

          {/* Info Box */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-8">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-emerald-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-emerald-900">نظام تحليل الأبحاث الطبية</h3>
                <p className="text-emerald-800 text-sm mt-1">
                  يقوم هذا النظام بتحليل الأبحاث الطبية من الجامعات المرموقة باستخدام تقنيات الذكاء الاصطناعي المتقدمة.
                  يتم تحديث المحتوى بشكل يومي مع أحدث الأبحاث والتحليلات.
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-8 items-center justify-center bg-gray-50 rounded-xl p-6">
            {/* QR Code Section */}
            <div className="flex flex-col items-center gap-4">
              <div className="bg-white p-6 rounded-xl shadow-md border-2 border-emerald-100">
                <QRCodeSVG
                  value={qrCodeUrl}
                  size={240}
                  level="H"
                  includeMargin={true}
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => window.location.href = dynamicPdfUrl}
                  className="flex items-center gap-2 px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-lg"
                >
                  <FileDown className="w-5 h-5" />
                  تحميل التقرير
                </button>
                <button
                  onClick={handleCopyUrl}
                  className="flex items-center gap-2 px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <LinkIcon className="w-5 h-5" />
                  {copied ? 'تم النسخ!' : 'نسخ الرابط'}
                </button>
              </div>
            </div>

            {/* Instructions */}
            <div className="max-w-sm text-right">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">تعليمات الاستخدام:</h2>
              <ul className="text-gray-600 space-y-3 list-none">
                <li className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-sm">١</span>
                  <span>امسح رمز QR باستخدام هاتفك</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-sm">٢</span>
                  <span>سيتم تحميل أحدث تقرير تلقائياً</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-sm">٣</span>
                  <span>يتم تحديث التقرير يومياً مع أحدث الأبحاث</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-sm">٤</span>
                  <span>لا حاجة لتحديث رمز QR - يشير دائماً إلى أحدث إصدار</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Features */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 text-right">
            <div className="p-4 bg-emerald-50 rounded-lg">
              <h3 className="font-semibold text-emerald-800 mb-2">تحليل متقدم</h3>
              <p className="text-sm text-emerald-600">
                يستخدم النظام نماذج ذكاء اصطناعي متعددة لتحليل وتلخيص الأبحاث الطبية
              </p>
            </div>
            <div className="p-4 bg-emerald-50 rounded-lg">
              <h3 className="font-semibold text-emerald-800 mb-2">تحديث مستمر</h3>
              <p className="text-sm text-emerald-600">
                يتم تحديث قاعدة البيانات يومياً مع أحدث الأبحاث من الجامعات العالمية
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
