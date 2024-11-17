export const Pulse = ({ color }: { color: string }) => {
  return (
    <span className="relative flex h-4 w-4">
      <span
        className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${color}`}
      />
      <span className={`relative inline-flex rounded-full h-4 w-4 ${color}`} />
    </span>
  );
};
