import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";


export default function Home() {
  return (
    <Layout>
    <div className="background-img con bc-h-100">
      <img
        className="stroke"
        role="img"
        src="https://library-sdb.apps.bancolombia.com/assets/1.2.0/strokes/06.svg"
      />
    </div>

    <div className="bg-dark">
      <div className="bc-container-16 bc-py-5">
        <div className="bc-row bc-align-items-center ">
          <div className="bc-mx-3">
            <h1 className="bc-text-brand-primary-01 bc-cibsans-font-style-12-bold ">
              DevSecOps Engine Backend
            </h1>
            <h2 className="bc-text-brand-primary-01 bc-cibsans-font-style-8-bold ">
              Somos parte de la revolución del código abierto
            </h2>
            <p className="bc-cibsans-font-style-7-extralight bc-text-brand-primary-01">
              Tu tambien tienes algo para contribuir.
            </p>
          </div>
          <div className="bc-me-5"></div>
          <div className="bc-mx-3 row-col">
                <Link
                  className="bc-button bc-button-primary bc-text-center bc-me-3 bc-mb-3 min-width-fit"
                  to="/docs/intro"
                >
                  Empezemos!
                </Link>
          </div>
        </div>
      </div>
    </div>
    <main></main>
  </Layout>
  );
}