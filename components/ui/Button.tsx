import Link from "next/link";
import type { ReactNode } from "react";

type BaseButtonProps = {
  children: ReactNode;
  className?: string;
};

type ButtonAsButtonProps = BaseButtonProps & {
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  href?: never;
};

type ButtonAsLinkProps = BaseButtonProps & {
  href: string;
  onClick?: never;
  type?: never;
};

type ButtonProps = ButtonAsButtonProps | ButtonAsLinkProps;

const baseClassName =
  "inline-flex items-center justify-center rounded-xl bg-[#009EDB] px-4 py-2 text-sm font-medium text-white transition-colors duration-200 hover:bg-[#007fb1]";

export function Button(props: ButtonProps) {
  if ("href" in props) {
    return (
      <Link href={props.href} className={`${baseClassName} ${props.className ?? ""}`}>
        {props.children}
      </Link>
    );
  }

  return (
    <button
      type={props.type ?? "button"}
      onClick={props.onClick}
      className={`${baseClassName} ${props.className ?? ""}`}
    >
      {props.children}
    </button>
  );
}
