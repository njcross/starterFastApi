import React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

export default function Button({ variant = "primary", ...props }: Props) {
  return (
    <button
      {...props}
      className={`btn ${variant === "ghost" ? "btn-ghost" : "btn-primary"} ${props.className ?? ""}`}
    />
  );
}
