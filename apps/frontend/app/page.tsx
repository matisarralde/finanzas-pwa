export default function Home() {
  return (
    <main style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
        {process.env.NEXT_PUBLIC_APP_NAME || "Finanzas PWA"}
      </h1>
      <p>Build OK. Luego conectamos Dashboard y el resto del UI.</p>
    </main>
  );
}
