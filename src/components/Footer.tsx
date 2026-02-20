const Footer = () => {
  return (
    <footer className="relative py-10 border-t border-border">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <span className="font-display text-xl font-bold text-primary">LARA</span>
            <span className="text-muted-foreground text-sm">Therapy System</span>
          </div>

          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-primary transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-primary transition-colors">Documentation</a>
          </div>

          <p className="text-muted-foreground text-sm">
            © 2024 LARA Research Group
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
